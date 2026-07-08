"""Map parsed C facts to an approximate Simulink-oriented IR."""

from __future__ import annotations

from dataclasses import dataclass
import logging
import re

from .c_parser import Assignment, ParsedCProject, SimulinkTrace
from .ir import BlockIR, ConnectionIR, ModelIR, ParameterIR, SignalIR

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class VariableRef:
    role: str
    name: str
    raw: str


class CToSimulinkMapper:
    def __init__(
        self,
        model_name: str,
        fallback_matlab_functions: bool = False,
    ) -> None:
        self.model_name = model_name
        self.fallback_matlab_functions = fallback_matlab_functions
        self.param_by_name: dict[str, ParameterIR] = {}
        self.block_by_output: dict[str, str] = {}
        self.block_by_id: dict[str, BlockIR] = {}
        self.synthetic_index = 0
        self.execution_index = 0
        self.warnings: list[str] = []

    def build(self, parsed: ParsedCProject) -> ModelIR:
        ir = ModelIR(
            model_name=self.model_name,
            original_model_name=parsed.model_name,
        )
        ir.warnings.extend(parsed.warnings)
        ir.annotations.append(
            "This model is inferred from generated C code. Simulink Coder output "
            "is not lossless; names, hierarchy, masks, sample times, solver "
            "settings, and annotations may differ from the original model."
        )

        self._collect_struct_signals(parsed, ir)
        self._collect_parameters(parsed, ir)
        self._create_input_output_blocks(ir)
        self._map_functions(parsed, ir)
        self._connect_blocks(ir)
        ir.warnings.extend(self.warnings)
        ir.blocks = sorted(ir.blocks, key=lambda block: (block.execution_index, block.id))
        ir.connections = sorted(
            set(ir.connections),
            key=lambda conn: (conn.dst, conn.dst_port, conn.src, conn.src_port),
        )
        return ir

    def _collect_struct_signals(self, parsed: ParsedCProject, ir: ModelIR) -> None:
        for struct in parsed.structs:
            if struct.kind == "inputs":
                for field in struct.fields:
                    ir.inputs.append(
                        SignalIR(field.name, "input", field.ctype, field.source_ref, "certain")
                    )
                    LOGGER.info("Input detected: %s", field.name)
            elif struct.kind == "outputs":
                for field in struct.fields:
                    ir.outputs.append(
                        SignalIR(field.name, "output", field.ctype, field.source_ref, "certain")
                    )
                    LOGGER.info("Output detected: %s", field.name)
            elif struct.kind == "block_signals":
                for field in struct.fields:
                    ir.signals.append(
                        SignalIR(field.name, "signal", field.ctype, field.source_ref, "certain")
                    )
            elif struct.kind in {"continuous_states", "dwork_states"}:
                for field in struct.fields:
                    ir.states.append(
                        SignalIR(field.name, "state", field.ctype, field.source_ref, "certain")
                    )

    def _collect_parameters(self, parsed: ParsedCProject, ir: ModelIR) -> None:
        for parameter in parsed.parameters:
            param_ir = ParameterIR(
                name=parameter.name,
                value=parameter.value,
                expression=parameter.expression,
                source_ref=parameter.source_ref,
                certainty="certain",
            )
            ir.parameters.append(param_ir)
            self.param_by_name[param_ir.name] = param_ir
            LOGGER.debug("Parameter detected: %s=%s", param_ir.name, param_ir.value)

    def _create_input_output_blocks(self, ir: ModelIR) -> None:
        for index, signal in enumerate(ir.inputs, start=1):
            block = self._new_block(
                ir,
                name=signal.name,
                block_type="Inport",
                output=f"input:{signal.name}",
                parameters={"Port": str(index)},
                source_ref=signal.source_ref,
                certainty="certain",
            )
            self.block_by_output[f"input:{signal.name}"] = block.id

        for index, signal in enumerate(ir.outputs, start=1):
            block = self._new_block(
                ir,
                name=signal.name,
                block_type="Outport",
                output=f"output:{signal.name}",
                parameters={"Port": str(index)},
                source_ref=signal.source_ref,
                certainty="certain",
            )
            self.block_by_output[f"output:{signal.name}"] = block.id

    def _map_functions(self, parsed: ParsedCProject, ir: ModelIR) -> None:
        for function in sorted(parsed.functions, key=lambda fn: (fn.source_file, fn.line)):
            if not (
                function.is_step
                or function.is_initialize
                or function.is_derivatives
                or function.is_terminate
            ):
                LOGGER.debug("Skipping support function %s", function.name)
                continue

            local_env: dict[str, str] = {}
            for assignment in function.assignments:
                target_ref = self._normalize_ref(assignment.target)
                if target_ref.role == "local":
                    if assignment.operator == "=":
                        local_env[target_ref.name] = self._resolve_locals(
                            assignment.expression, local_env
                        )
                    continue

                if function.is_initialize:
                    self._map_initialize_assignment(assignment, target_ref, ir)
                    continue

                if function.is_derivatives:
                    self._map_derivative_assignment(assignment, target_ref, local_env, ir)
                    continue

                self._map_step_assignment(assignment, target_ref, local_env, ir)

    def _map_initialize_assignment(
        self, assignment: Assignment, target_ref: VariableRef, ir: ModelIR
    ) -> None:
        if target_ref.role not in {"state", "dwork_state"}:
            return
        expr_ref = self._normalize_ref(assignment.expression)
        if expr_ref.role == "parameter":
            param = self.param_by_name.get(expr_ref.name)
            for block in ir.blocks:
                if block.output and block.output.endswith(target_ref.name.replace("_DSTATE", "")):
                    block.parameters.setdefault(
                        "InitialCondition", self._param_value_or_name(param, expr_ref.name)
                    )

    def _map_derivative_assignment(
        self,
        assignment: Assignment,
        target_ref: VariableRef,
        local_env: dict[str, str],
        ir: ModelIR,
    ) -> None:
        if target_ref.role not in {"state_derivative", "state"}:
            return
        expression = self._resolve_locals(assignment.expression, local_env)
        state_name = target_ref.name
        block_id = self._find_integrator_for_state(state_name, ir)
        if not block_id:
            annotation = (
                f"Inferred derivative update at {assignment.source_file}:{assignment.line}: "
                f"{assignment.target} = {assignment.expression}"
            )
            ir.annotations.append(annotation)
            LOGGER.info("Unmapped derivative: %s", annotation)
            return
        block = self.block_by_id[block_id]
        for dep in self._extract_dependencies(expression):
            self._append_unique(block.inputs, self._dep_key(dep))
        block.expression = expression

    def _map_step_assignment(
        self,
        assignment: Assignment,
        target_ref: VariableRef,
        local_env: dict[str, str],
        ir: ModelIR,
    ) -> None:
        if target_ref.role not in {"signal", "output", "state", "dwork_state"}:
            return

        expression = self._resolve_locals(assignment.expression, local_env)
        trace = assignment.trace
        block_type = self._block_type_for_assignment(assignment, expression)

        if block_type in {"Skip", "ClockInfrastructure"}:
            return

        if target_ref.role == "output":
            self._map_output_assignment(assignment, target_ref, expression, ir)
            return

        if target_ref.role == "dwork_state":
            self._map_state_update(assignment, target_ref, expression, ir)
            return

        if self._is_duplicate_semantic_assignment(target_ref.name, block_type, ir):
            return

        if block_type == "Unknown" and not self.fallback_matlab_functions:
            ir.annotations.append(
                f"Unmapped assignment at {assignment.source_file}:{assignment.line}: "
                f"{assignment.target} {assignment.operator} {assignment.expression}"
            )
            LOGGER.info("Unmapped assignment preserved as annotation: %s", assignment.statement)
            return

        block = self._create_block_from_assignment(
            assignment, target_ref, expression, block_type, trace, local_env, ir
        )
        if block.output:
            self.block_by_output[block.output] = block.id
        LOGGER.info(
            "Inferred block %s (%s) from %s:%d",
            block.name,
            block.block_type,
            assignment.source_file,
            assignment.line,
        )

    def _map_output_assignment(
        self,
        assignment: Assignment,
        target_ref: VariableRef,
        expression: str,
        ir: ModelIR,
    ) -> None:
        block_id = self.block_by_output.get(f"output:{target_ref.name}")
        if not block_id:
            block = self._new_block(
                ir,
                name=target_ref.name,
                block_type="Outport",
                output=f"output:{target_ref.name}",
                source_ref=assignment.trace.path if assignment.trace else None,
                certainty="certain",
            )
            block_id = block.id
            self.block_by_output[f"output:{target_ref.name}"] = block.id
        block = self.block_by_id[block_id]
        for dep in self._extract_dependencies(expression):
            self._append_unique(block.inputs, self._dep_key(dep))
        block.expression = expression
        block.source_line = assignment.line
        block.source_function = assignment.function_name

    def _map_state_update(
        self,
        assignment: Assignment,
        target_ref: VariableRef,
        expression: str,
        ir: ModelIR,
    ) -> None:
        trace = assignment.trace
        if trace and "UnitDelay" in trace.kind.replace(" ", ""):
            existing = self._find_block_by_source_ref(trace.path, ir)
            if existing:
                for dep in self._extract_dependencies(expression):
                    self._append_unique(existing.inputs, self._dep_key(dep))
                existing.parameters.setdefault("InitialCondition", "0")
                return
        ir.annotations.append(
            f"State update at {assignment.source_file}:{assignment.line} inferred from C: "
            f"{assignment.target} {assignment.operator} {assignment.expression}"
        )

    def _create_block_from_assignment(
        self,
        assignment: Assignment,
        target_ref: VariableRef,
        expression: str,
        block_type: str,
        trace: SimulinkTrace | None,
        local_env: dict[str, str],
        ir: ModelIR,
    ) -> BlockIR:
        source_ref = trace.path if trace else None
        name = self._name_from_trace_or_target(trace, target_ref.name)
        params: dict[str, str] = {}
        inputs: list[str] = []

        if block_type == "Gain":
            signal_deps, param_deps, literals = self._split_dependencies(expression)
            gain_value = self._gain_value(expression, param_deps, literals)
            params["Gain"] = gain_value
            inputs = [self._dep_key(dep) for dep in signal_deps[:1]]
        elif block_type == "Sum":
            deps = self._extract_dependencies(expression)
            inputs = [self._dep_key(dep) for dep in deps]
            params["Inputs"] = self._sum_inputs_string(expression, deps)
        elif block_type == "Product":
            deps = self._extract_dependencies(expression)
            inputs = [self._dep_key(dep) for dep in deps]
            params["Inputs"] = self._product_inputs_string(expression, deps)
        elif block_type == "Constant":
            params["Value"] = self._constant_value(expression)
        elif block_type == "Saturation":
            signal_expr = local_env.get("u0", expression)
            lower_expr = local_env.get("u1")
            upper_expr = local_env.get("u2")
            for dep in self._extract_dependencies(signal_expr):
                if dep.role in {"signal", "input", "state", "dwork_state", "parameter"}:
                    inputs.append(self._dep_key(dep))
            params["LowerLimit"] = self._value_from_expression(lower_expr, default="-inf")
            params["UpperLimit"] = self._value_from_expression(upper_expr, default="inf")
        elif block_type == "Step":
            base = target_ref.name
            params["Time"] = self._param_value_by_candidates([f"{base}_Time"], "0")
            params["Before"] = self._param_value_by_candidates([f"{base}_Y0"], "0")
            params["After"] = self._param_value_by_candidates([f"{base}_YFinal"], "1")
        elif block_type in {"Integrator", "Discrete-Time Integrator"}:
            deps = [
                dep
                for dep in self._extract_dependencies(expression)
                if dep.role in {"state", "dwork_state", "signal", "input"}
            ]
            if deps and deps[0].role in {"state", "dwork_state"}:
                params["StateName"] = deps[0].name
            params["InitialCondition"] = self._initial_condition_for(target_ref.name)
        elif block_type == "Unit Delay":
            deps = self._extract_dependencies(expression)
            state_deps = [dep for dep in deps if dep.role in {"state", "dwork_state"}]
            if state_deps:
                params["StateName"] = state_deps[0].name
            params["InitialCondition"] = self._initial_condition_for(target_ref.name)
        elif block_type == "PassThrough":
            deps = self._extract_dependencies(expression)
            inputs = [self._dep_key(dep) for dep in deps[:1]]
        else:
            deps = self._extract_dependencies(expression)
            inputs = [self._dep_key(dep) for dep in deps]
            block_type = "MATLAB Function" if self.fallback_matlab_functions else "Annotation"

        block = self._new_block(
            ir,
            name=name,
            block_type=block_type,
            output=f"signal:{target_ref.name}",
            inputs=inputs,
            parameters=params,
            source_ref=source_ref,
            source_function=assignment.function_name,
            source_line=assignment.line,
            expression=expression,
            unmapped_code=assignment.statement if block_type in {"MATLAB Function", "Annotation"} else None,
            certainty="certain" if trace else "inferred",
        )
        return block

    def _connect_blocks(self, ir: ModelIR) -> None:
        for block in list(ir.blocks):
            if block.block_type in {"Inport", "Constant"}:
                continue
            for port, input_key in enumerate(block.inputs, start=1):
                src_id = self._source_block_for_input(input_key, ir)
                if not src_id:
                    self.warnings.append(
                        f"No source block found for {input_key} feeding {block.name}"
                    )
                    continue
                ir.connections.append(
                    ConnectionIR(
                        src=src_id,
                        dst=block.id,
                        src_port=1,
                        dst_port=port,
                        signal=input_key,
                        inferred=True,
                        reason="dependency inferred from generated C expression",
                    )
                )

    def _source_block_for_input(self, input_key: str, ir: ModelIR) -> str | None:
        if input_key in self.block_by_output:
            return self.block_by_output[input_key]
        role, _, name = input_key.partition(":")
        if role == "input":
            return self.block_by_output.get(input_key)
        if role == "parameter":
            return self._constant_block_for_parameter(name, ir).id
        if role in {"signal", "state", "dwork_state"}:
            return self.block_by_output.get(f"signal:{name}") or self.block_by_output.get(
                f"state:{name}"
            )
        return None

    def _constant_block_for_parameter(self, name: str, ir: ModelIR) -> BlockIR:
        output_key = f"parameter:{name}"
        if output_key in self.block_by_output:
            return self.block_by_id[self.block_by_output[output_key]]

        param = self.param_by_name.get(name)
        source_ref = param.source_ref if param else None
        value = self._param_value_or_name(param, name)
        block = self._new_block(
            ir,
            name=self._unique_block_name(f"Const_{name}", ir),
            block_type="Constant",
            output=output_key,
            parameters={"Value": value},
            source_ref=source_ref,
            certainty="inferred",
        )
        self.block_by_output[output_key] = block.id
        return block

    def _block_type_for_assignment(self, assignment: Assignment, expression: str) -> str:
        trace_kind = assignment.trace.kind if assignment.trace else ""
        compact_kind = trace_kind.replace(" ", "").lower()
        if any(word in compact_kind for word in ["matfilelogging", "registrationcode"]):
            return "Skip"
        if "outport" in compact_kind:
            return "Outport"
        if "saturate" in compact_kind or "saturation" in compact_kind:
            return "Saturation"
        if "unitdelay" in compact_kind:
            return "Unit Delay"
        if "delay" in compact_kind and "integrator" not in compact_kind:
            return "Unit Delay"
        if "discrete-timeintegrator" in compact_kind:
            return "Discrete-Time Integrator"
        if "integrator" in compact_kind:
            return "Integrator"
        if compact_kind == "gain" or compact_kind.endswith("/gain"):
            return "Gain"
        if "gain" in compact_kind:
            return "Gain"
        if "sum" in compact_kind:
            return "Sum"
        if "product" in compact_kind:
            return "Product"
        if "constant" in compact_kind:
            return "Constant"
        if "step" in compact_kind:
            return "Step"
        if "switch" in compact_kind:
            return "Switch"

        inferred = self._infer_block_type_from_expression(expression)
        LOGGER.debug(
            "Inferred block type %s for %s = %s",
            inferred,
            assignment.target,
            expression,
        )
        return inferred

    def _infer_block_type_from_expression(self, expression: str) -> str:
        deps = self._extract_dependencies(expression)
        if self._is_numeric_literal(expression) or (
            len(deps) == 1 and deps[0].role == "parameter"
        ):
            return "Constant"
        if len(deps) == 1 and self._is_single_dependency_expression(expression, deps[0]):
            return "PassThrough"
        if self._looks_like_gain(expression, deps):
            return "Gain"
        if self._has_top_level_operator(expression, ["+", "-"]):
            return "Sum"
        if self._has_top_level_operator(expression, ["*", "/"]):
            return "Product"
        return "Unknown"

    def _normalize_ref(self, token: str) -> VariableRef:
        raw = token.strip()
        raw = raw.strip("()")
        raw = re.sub(r"^\(\s*[A-Za-z_]\w*(?:\s*\*)?\s*\)\s*", "", raw)
        raw = raw.replace("->", ".")

        for role, suffix in [
            ("signal", "_B"),
            ("output", "_Y"),
            ("input", "_U"),
            ("parameter", "_P"),
            ("state", "_X"),
            ("dwork_state", "_DW"),
        ]:
            match = re.search(
                rf"\b[A-Za-z_]\w*{re.escape(suffix)}\.([A-Za-z_]\w*)\b", raw
            )
            if match:
                return VariableRef(role=role, name=match.group(1), raw=token)

        match = re.search(r"\b_rtXdot\.([A-Za-z_]\w*)\b", raw)
        if match:
            return VariableRef("state_derivative", match.group(1), token)
        match = re.search(r"\b_rtXdot->([A-Za-z_]\w*)\b", token)
        if match:
            return VariableRef("state_derivative", match.group(1), token)

        simple = re.fullmatch(r"[A-Za-z_]\w*", raw)
        if simple:
            return VariableRef("local", raw, token)
        return VariableRef("unknown", raw, token)

    def _extract_dependencies(self, expression: str) -> list[VariableRef]:
        deps: list[VariableRef] = []
        seen: set[str] = set()
        patterns = [
            ("signal", r"\b[A-Za-z_]\w*_B\.([A-Za-z_]\w*)\b"),
            ("output", r"\b[A-Za-z_]\w*_Y\.([A-Za-z_]\w*)\b"),
            ("input", r"\b[A-Za-z_]\w*_U\.([A-Za-z_]\w*)\b"),
            ("parameter", r"\b[A-Za-z_]\w*_P\.([A-Za-z_]\w*)\b"),
            ("state", r"\b[A-Za-z_]\w*_X\.([A-Za-z_]\w*)\b"),
            ("dwork_state", r"\b[A-Za-z_]\w*_DW\.([A-Za-z_]\w*)\b"),
            ("state_derivative", r"\b_rtXdot(?:->|\.)\s*([A-Za-z_]\w*)\b"),
        ]
        matches: list[tuple[int, VariableRef]] = []
        for role, pattern in patterns:
            for match in re.finditer(pattern, expression):
                ref = VariableRef(role=role, name=match.group(1), raw=match.group(0))
                key = self._dep_key(ref)
                if key in seen:
                    continue
                seen.add(key)
                matches.append((match.start(), ref))
        for _, ref in sorted(matches, key=lambda item: item[0]):
            deps.append(ref)
        return deps

    def _split_dependencies(
        self, expression: str
    ) -> tuple[list[VariableRef], list[VariableRef], list[str]]:
        deps = self._extract_dependencies(expression)
        signal_deps = [
            dep for dep in deps if dep.role in {"signal", "input", "state", "dwork_state"}
        ]
        param_deps = [dep for dep in deps if dep.role == "parameter"]
        without_refs = expression
        for dep in deps:
            without_refs = without_refs.replace(dep.raw, " ")
        literals = re.findall(
            r"(?<![A-Za-z_])[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?",
            without_refs,
        )
        return signal_deps, param_deps, literals

    def _resolve_locals(self, expression: str, local_env: dict[str, str]) -> str:
        resolved = expression
        for _ in range(3):
            changed = False
            for name, value in sorted(local_env.items(), key=lambda item: -len(item[0])):
                new = re.sub(rf"\b{re.escape(name)}\b", f"({value})", resolved)
                if new != resolved:
                    resolved = new
                    changed = True
            if not changed:
                break
        return resolved

    def _gain_value(
        self, expression: str, param_deps: list[VariableRef], literals: list[str]
    ) -> str:
        if param_deps:
            param = self.param_by_name.get(param_deps[0].name)
            return self._param_value_or_name(param, param_deps[0].name)
        if literals:
            return literals[0]
        return expression

    def _constant_value(self, expression: str) -> str:
        deps = self._extract_dependencies(expression)
        if len(deps) == 1 and deps[0].role == "parameter":
            return self._value_from_expression(deps[0].raw, default=deps[0].name)
        if self._is_numeric_literal(expression):
            return expression
        return expression

    def _value_from_expression(self, expression: str | None, default: str) -> str:
        if not expression:
            return default
        deps = self._extract_dependencies(expression)
        if len(deps) == 1 and expression.strip("() ") == deps[0].raw:
            if deps[0].role == "parameter":
                param = self.param_by_name.get(deps[0].name)
                return self._param_value_or_name(param, deps[0].name)
        if self._is_numeric_literal(expression):
            return expression
        return expression

    def _param_value_by_candidates(self, candidates: list[str], default: str) -> str:
        for candidate in candidates:
            param = self.param_by_name.get(candidate)
            if param and param.value is not None:
                return param.value
        return default

    def _param_value_or_name(self, param: ParameterIR | None, name: str) -> str:
        if param and param.value not in {None, ""}:
            return param.value
        return name

    def _initial_condition_for(self, signal_name: str) -> str:
        candidates = [
            f"{signal_name}_IC",
            f"{signal_name.replace('_CSTATE', '')}_IC",
            f"{signal_name.replace('_DSTATE', '')}_InitialCondition",
            f"{signal_name.replace('_DSTATE', '')}_IC",
        ]
        return self._param_value_by_candidates(candidates, "0")

    def _find_integrator_for_state(self, state_name: str, ir: ModelIR) -> str | None:
        for block in ir.blocks:
            if block.block_type in {"Integrator", "Discrete-Time Integrator"}:
                state_param = block.parameters.get("StateName", "")
                if state_param == state_name:
                    return block.id
                if state_param.replace("_CSTATE", "") == state_name.replace("_CSTATE", ""):
                    return block.id
                if block.output and block.output.endswith(state_name.replace("_CSTATE", "")):
                    return block.id
        return None

    def _find_block_by_source_ref(self, source_ref: str, ir: ModelIR) -> BlockIR | None:
        for block in ir.blocks:
            if block.source_ref == source_ref:
                return block
        return None

    def _is_duplicate_semantic_assignment(
        self, output_name: str, block_type: str, ir: ModelIR
    ) -> bool:
        output_key = f"signal:{output_name}"
        existing_id = self.block_by_output.get(output_key)
        if not existing_id:
            return False
        existing = self.block_by_id[existing_id]
        return existing.block_type == block_type

    def _is_single_dependency_expression(self, expression: str, dep: VariableRef) -> bool:
        return expression.strip("() ") == dep.raw

    def _looks_like_gain(self, expression: str, deps: list[VariableRef]) -> bool:
        if "*" not in expression:
            return False
        roles = {dep.role for dep in deps}
        if "parameter" in roles and roles & {"signal", "input", "state", "dwork_state"}:
            return True
        if len([dep for dep in deps if dep.role in {"signal", "input", "state"}]) == 1:
            without_deps = expression
            for dep in deps:
                without_deps = without_deps.replace(dep.raw, " ")
            return bool(re.search(r"\d", without_deps))
        return False

    def _has_top_level_operator(self, expression: str, operators: list[str]) -> bool:
        depth = 0
        for char in expression:
            if char == "(":
                depth += 1
            elif char == ")" and depth:
                depth -= 1
            elif depth == 0 and char in operators:
                return True
        if not any(char in expression for char in operators):
            return False
        return True

    def _sum_inputs_string(self, expression: str, deps: list[VariableRef]) -> str:
        if len(deps) <= 1:
            return "++"
        signs: list[str] = []
        for dep in deps:
            dep_index = expression.find(dep.raw)
            prefix = expression[:dep_index].rstrip()
            signs.append("-" if prefix.endswith("-") else "+")
        return "".join(signs) if len(signs) >= 2 else "++"

    def _product_inputs_string(self, expression: str, deps: list[VariableRef]) -> str:
        if len(deps) <= 1:
            return "**"
        signs: list[str] = []
        for dep in deps:
            dep_index = expression.find(dep.raw)
            prefix = expression[:dep_index].rstrip()
            signs.append("/" if prefix.endswith("/") else "*")
        return "".join(signs) if len(signs) >= 2 else "**"

    @staticmethod
    def _is_numeric_literal(value: str) -> bool:
        return bool(
            re.fullmatch(
                r"\(?\s*[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?[fFlL]?\s*\)?",
                value.strip(),
            )
        )

    def _name_from_trace_or_target(self, trace: SimulinkTrace | None, target_name: str) -> str:
        if trace and trace.path:
            cleaned = trace.path.replace("<", "").replace(">", "")
            cleaned = cleaned.replace("/", "_")
            return cleaned
        return target_name

    def _new_block(
        self,
        ir: ModelIR,
        name: str,
        block_type: str,
        output: str | None = None,
        inputs: list[str] | None = None,
        parameters: dict[str, str] | None = None,
        source_ref: str | None = None,
        source_function: str | None = None,
        source_line: int | None = None,
        expression: str | None = None,
        unmapped_code: str | None = None,
        certainty: str = "inferred",
    ) -> BlockIR:
        unique_name = self._unique_block_name(name, ir)
        self.execution_index += 1
        block = BlockIR(
            id=unique_name,
            name=unique_name,
            block_type=block_type,
            output=output,
            inputs=inputs or [],
            parameters=parameters or {},
            source_ref=source_ref,
            source_function=source_function,
            source_line=source_line,
            expression=expression,
            unmapped_code=unmapped_code,
            certainty=certainty,
            execution_index=self.execution_index,
        )
        ir.blocks.append(block)
        self.block_by_id[block.id] = block
        if output:
            self.block_by_output[output] = block.id
        return block

    def _unique_block_name(self, proposed: str, ir: ModelIR) -> str:
        base = self._sanitize_name(proposed)
        existing = {block.name for block in ir.blocks}
        if base not in existing:
            return base
        suffix = 2
        while f"{base}_{suffix}" in existing:
            suffix += 1
        return f"{base}_{suffix}"

    @staticmethod
    def _sanitize_name(name: str) -> str:
        name = re.sub(r"[^A-Za-z0-9_]+", "_", name.strip())
        name = re.sub(r"_+", "_", name).strip("_")
        if not name:
            name = "Block"
        if name[0].isdigit():
            name = f"b_{name}"
        return name[:80]

    @staticmethod
    def _dep_key(dep: VariableRef) -> str:
        if dep.role == "parameter":
            return f"parameter:{dep.name}"
        if dep.role == "input":
            return f"input:{dep.name}"
        if dep.role in {"state", "dwork_state"}:
            return f"{dep.role}:{dep.name}"
        return f"signal:{dep.name}"

    @staticmethod
    def _append_unique(items: list[str], value: str) -> None:
        if value not in items:
            items.append(value)
