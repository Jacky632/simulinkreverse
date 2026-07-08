"""Tolerant C parser for common Simulink Coder output patterns."""

from __future__ import annotations

from dataclasses import dataclass, field
import logging
import re

from .loader import SourceFile

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class StructField:
    ctype: str
    name: str
    array_suffix: str = ""
    comment: str = ""
    source_ref: str | None = None
    expression: str | None = None


@dataclass(frozen=True)
class StructDef:
    name: str
    fields: list[StructField]
    source_file: str
    line: int
    kind: str = "unknown"


@dataclass(frozen=True)
class SimulinkTrace:
    kind: str
    path: str
    text: str
    offset: int
    line: int


@dataclass(frozen=True)
class Assignment:
    target: str
    operator: str
    expression: str
    statement: str
    source_file: str
    line: int
    function_name: str
    index: int
    trace: SimulinkTrace | None = None


@dataclass(frozen=True)
class FunctionCall:
    name: str
    statement: str
    source_file: str
    line: int
    function_name: str


@dataclass
class FunctionDef:
    name: str
    return_type: str
    args: str
    body: str
    source_file: str
    line: int
    assignments: list[Assignment] = field(default_factory=list)
    calls: list[FunctionCall] = field(default_factory=list)
    traces: list[SimulinkTrace] = field(default_factory=list)

    @property
    def is_step(self) -> bool:
        return self.name.endswith("_step") or self.name == "step"

    @property
    def is_initialize(self) -> bool:
        return self.name.endswith("_initialize") or self.name == "initialize"

    @property
    def is_terminate(self) -> bool:
        return self.name.endswith("_terminate") or self.name == "terminate"

    @property
    def is_derivatives(self) -> bool:
        return self.name.endswith("_derivatives") or self.name == "derivatives"


@dataclass(frozen=True)
class ParameterValue:
    name: str
    value: str | None
    expression: str | None
    source_ref: str | None
    comment: str


@dataclass
class ParsedCProject:
    source_files: list[SourceFile]
    model_name: str | None
    functions: list[FunctionDef]
    structs: list[StructDef]
    parameters: list[ParameterValue]
    warnings: list[str] = field(default_factory=list)

    def function_by_name(self, name: str) -> FunctionDef | None:
        for function in self.functions:
            if function.name == name:
                return function
        return None


class CParser:
    """Extract function, struct, assignment, and parameter facts from C text.

    This is intentionally not a full C compiler front end. Generated Simulink C
    is regular enough that brace matching plus trace comments gives useful,
    deterministic results while remaining dependency-free.
    """

    FUNCTION_RE = re.compile(
        r"(?m)^[ \t]*(?P<return>(?:(?:static|extern)\s+)?[A-Za-z_][\w\s\*\(\)]*?)"
        r"\s+(?P<name>[A-Za-z_]\w*)\s*\((?P<args>[^;{}]*)\)\s*\{"
    )
    TYPEDEF_STRUCT_RE = re.compile(
        r"typedef\s+struct(?:\s+[A-Za-z_]\w*)?\s*\{(?P<body>.*?)\}\s*"
        r"(?P<name>[A-Za-z_]\w*)\s*;",
        re.S,
    )
    NAMED_STRUCT_RE = re.compile(
        r"struct\s+(?P<name>[A-Za-z_]\w*)\s*\{(?P<body>.*?)\}\s*;",
        re.S,
    )
    TRACE_RE = re.compile(
        r"/\*(?P<text>.*?(?P<kind>[A-Za-z][A-Za-z0-9 _/\-]*?):\s*"
        r"'(?P<path>[^']+)'.*?)\*/",
        re.S,
    )
    ASSIGNMENT_RE = re.compile(
        r"^(?P<target>.+?)\s*(?P<op>\+=|-=|\*=|/=|=)\s*(?P<expr>.+)$",
        re.S,
    )
    CALL_RE = re.compile(r"\b(?P<name>[A-Za-z_]\w*)\s*\(")
    MODEL_NAME_RE = re.compile(r'Code generation for model\s+"(?P<name>[^"]+)"')
    IF_FOR_KEYWORDS = {"if", "for", "while", "switch", "return", "sizeof"}

    def parse(self, source_files: list[SourceFile]) -> ParsedCProject:
        warnings: list[str] = []
        structs: list[StructDef] = []
        functions: list[FunctionDef] = []
        model_name = self._find_model_name(source_files)

        for source in source_files:
            try:
                structs.extend(self._parse_structs(source))
            except Exception as exc:  # pragma: no cover - defensive logging
                msg = f"failed to parse structs in {source.relative_path}: {exc}"
                warnings.append(msg)
                LOGGER.warning(msg)

            try:
                functions.extend(self._parse_functions(source))
            except Exception as exc:  # pragma: no cover - defensive logging
                msg = f"failed to parse functions in {source.relative_path}: {exc}"
                warnings.append(msg)
                LOGGER.warning(msg)

        parameters = self._parse_parameters(source_files, structs)
        for function in functions:
            LOGGER.info(
                "Detected function %s in %s:%d with %d assignments",
                function.name,
                function.source_file,
                function.line,
                len(function.assignments),
            )

        return ParsedCProject(
            source_files=source_files,
            model_name=model_name,
            functions=functions,
            structs=structs,
            parameters=parameters,
            warnings=warnings,
        )

    def _find_model_name(self, source_files: list[SourceFile]) -> str | None:
        for source in source_files:
            match = self.MODEL_NAME_RE.search(source.text)
            if match:
                return match.group("name")
        for source in source_files:
            match = re.search(r"\bvoid\s+([A-Za-z_]\w*)_step\s*\(", source.text)
            if match:
                return match.group(1)
        return None

    def _parse_structs(self, source: SourceFile) -> list[StructDef]:
        structs: list[StructDef] = []
        occupied: list[tuple[int, int]] = []
        for match in self.TYPEDEF_STRUCT_RE.finditer(source.text):
            occupied.append((match.start(), match.end()))
            line = self._line_at(source.text, match.start())
            fields = self._parse_struct_fields(match.group("body"))
            structs.append(
                StructDef(
                    name=match.group("name"),
                    fields=fields,
                    source_file=source.relative_path,
                    line=line,
                    kind=self._classify_struct(match.group("name")),
                )
            )

        for match in self.NAMED_STRUCT_RE.finditer(source.text):
            if any(start <= match.start() < end for start, end in occupied):
                continue
            line = self._line_at(source.text, match.start())
            fields = self._parse_struct_fields(match.group("body"))
            structs.append(
                StructDef(
                    name=match.group("name"),
                    fields=fields,
                    source_file=source.relative_path,
                    line=line,
                    kind=self._classify_struct(match.group("name")),
                )
            )
        return structs

    def _parse_struct_fields(self, body: str) -> list[StructField]:
        fields: list[StructField] = []
        lines = body.splitlines()
        index = 0
        while index < len(lines):
            line = lines[index]
            field_match = re.match(
                r"^\s*(?P<ctype>(?:const\s+)?[A-Za-z_]\w*(?:\s+[*A-Za-z_]\w*)*)"
                r"\s+(?P<name>[A-Za-z_]\w*)"
                r"(?P<array>(?:\s*\[[^\]]+\])*)\s*;\s*(?P<tail>/\*.*)?$",
                line,
            )
            if not field_match:
                index += 1
                continue

            comment_parts: list[str] = []
            tail = field_match.group("tail")
            if tail:
                comment_parts.append(tail)
                while "*/" not in "\n".join(comment_parts) and index + 1 < len(lines):
                    index += 1
                    comment_parts.append(lines[index])

            comment = "\n".join(comment_parts)
            fields.append(
                StructField(
                    ctype=" ".join(field_match.group("ctype").split()),
                    name=field_match.group("name"),
                    array_suffix=field_match.group("array").strip(),
                    comment=comment,
                    source_ref=self._extract_referenced_by(comment),
                    expression=self._extract_expression(comment),
                )
            )
            index += 1
        return fields

    def _parse_functions(self, source: SourceFile) -> list[FunctionDef]:
        functions: list[FunctionDef] = []
        text_without_comments = self._mask_comments(source.text)
        for match in self.FUNCTION_RE.finditer(text_without_comments):
            name = match.group("name")
            if name in self.IF_FOR_KEYWORDS:
                continue
            open_brace = match.end() - 1
            close_brace = self._find_matching_brace(text_without_comments, open_brace)
            if close_brace is None:
                LOGGER.warning(
                    "Could not find closing brace for function %s in %s:%d",
                    name,
                    source.relative_path,
                    self._line_at(source.text, match.start()),
                )
                continue
            body = source.text[open_brace + 1 : close_brace]
            function = FunctionDef(
                name=name,
                return_type=" ".join(match.group("return").split()),
                args=" ".join(match.group("args").split()),
                body=body,
                source_file=source.relative_path,
                line=self._line_at(source.text, match.start()),
            )
            self._parse_function_body(function)
            functions.append(function)
        return functions

    def _parse_function_body(self, function: FunctionDef) -> None:
        traces: list[SimulinkTrace] = []
        for trace_match in self.TRACE_RE.finditer(function.body):
            trace = SimulinkTrace(
                kind=self._normalize_trace_kind(trace_match.group("kind")),
                path=trace_match.group("path").strip(),
                text=" ".join(trace_match.group("text").split()),
                offset=trace_match.start(),
                line=function.line + self._line_at(function.body, trace_match.start()) - 1,
            )
            traces.append(trace)
        function.traces = traces

        masked = self._mask_comments(function.body)
        assignments: list[Assignment] = []
        calls: list[FunctionCall] = []
        for statement, start in self._iter_statements(masked):
            statement_clean = self._clean_statement(statement)
            if not statement_clean:
                continue
            line = function.line + self._line_at(function.body, start) - 1
            trace = self._nearest_trace(traces, start)
            assignment = self._parse_assignment(
                statement_clean,
                source_file=function.source_file,
                line=line,
                function_name=function.name,
                index=len(assignments),
                trace=trace,
            )
            if assignment:
                assignments.append(assignment)

            for call_match in self.CALL_RE.finditer(statement_clean):
                call_name = call_match.group("name")
                if call_name in self.IF_FOR_KEYWORDS:
                    continue
                calls.append(
                    FunctionCall(
                        name=call_name,
                        statement=statement_clean,
                        source_file=function.source_file,
                        line=line,
                        function_name=function.name,
                    )
                )

        function.assignments = assignments
        function.calls = calls

    def _iter_statements(self, body_without_comments: str) -> list[tuple[str, int]]:
        statements: list[tuple[str, int]] = []
        start = 0
        paren_depth = 0
        bracket_depth = 0
        for index, char in enumerate(body_without_comments):
            if char == "(":
                paren_depth += 1
            elif char == ")" and paren_depth:
                paren_depth -= 1
            elif char == "[":
                bracket_depth += 1
            elif char == "]" and bracket_depth:
                bracket_depth -= 1
            elif char == ";" and paren_depth >= 0 and bracket_depth >= 0:
                statement = body_without_comments[start : index + 1]
                brace_pos = max(statement.rfind("{"), statement.rfind("}"))
                statement_base = brace_pos + 1 if brace_pos >= 0 else 0
                trimmed = statement[statement_base:]
                leading = len(trimmed) - len(trimmed.lstrip())
                statements.append((trimmed, start + statement_base + leading))
                start = index + 1
        return statements

    def _parse_assignment(
        self,
        statement: str,
        source_file: str,
        line: int,
        function_name: str,
        index: int,
        trace: SimulinkTrace | None,
    ) -> Assignment | None:
        if statement.startswith(("if ", "for ", "while ", "switch ", "return ")):
            return None
        statement_no_semicolon = statement[:-1].strip() if statement.endswith(";") else statement
        match = self.ASSIGNMENT_RE.match(statement_no_semicolon)
        if not match:
            return None
        target = self._strip_declaration_prefix(match.group("target").strip())
        if not target or target.startswith(("if ", "for ", "while ")):
            return None
        expression = " ".join(match.group("expr").strip().split())
        if not expression:
            return None
        return Assignment(
            target=target,
            operator=match.group("op"),
            expression=expression,
            statement=statement,
            source_file=source_file,
            line=line,
            function_name=function_name,
            index=index,
            trace=trace,
        )

    def _parse_parameters(
        self, source_files: list[SourceFile], structs: list[StructDef]
    ) -> list[ParameterValue]:
        param_struct = self._select_parameter_struct(structs)
        if not param_struct:
            return []

        initializer_values = self._extract_parameter_initializer_values(source_files)
        parameters: list[ParameterValue] = []
        for index, field_def in enumerate(param_struct.fields):
            value = initializer_values[index] if index < len(initializer_values) else None
            parameters.append(
                ParameterValue(
                    name=field_def.name,
                    value=value,
                    expression=field_def.expression,
                    source_ref=field_def.source_ref,
                    comment=field_def.comment,
                )
            )
        return parameters

    def _select_parameter_struct(self, structs: list[StructDef]) -> StructDef | None:
        candidates = [struct for struct in structs if struct.kind == "parameters"]
        if not candidates:
            return None
        return max(candidates, key=lambda struct: len(struct.fields))

    def _extract_parameter_initializer_values(
        self, source_files: list[SourceFile]
    ) -> list[str]:
        for source in source_files:
            match = re.search(
                r"\bP_[A-Za-z_]\w*_T\s+[A-Za-z_]\w*_P\s*=\s*\{(?P<body>.*?)\}\s*;",
                source.text,
                re.S,
            )
            if not match:
                continue
            body = self._mask_comments(match.group("body"))
            values: list[str] = []
            for piece in body.split(","):
                cleaned = " ".join(piece.strip().split())
                if cleaned:
                    values.append(cleaned)
            return values
        return []

    @staticmethod
    def _mask_comments(text: str) -> str:
        def repl(match: re.Match[str]) -> str:
            return "\n".join(" " * len(line) for line in match.group(0).splitlines())

        text = re.sub(r"/\*.*?\*/", repl, text, flags=re.S)
        text = re.sub(r"//.*", lambda m: " " * len(m.group(0)), text)
        return text

    @staticmethod
    def _clean_statement(statement: str) -> str:
        return " ".join(statement.strip().split())

    @staticmethod
    def _strip_declaration_prefix(target: str) -> str:
        target = target.strip()
        target = re.sub(
            r"^(?:static\s+|const\s+|volatile\s+)*(?:real_T|time_T|int_T|uint_T|"
            r"boolean_T|char_T|double|float|int|unsigned|signed|long|short|"
            r"size_t)\s+",
            "",
            target,
        )
        target = target.strip()
        target = re.sub(r"^\*+", "", target).strip()
        return target

    @staticmethod
    def _line_at(text: str, offset: int) -> int:
        return text.count("\n", 0, offset) + 1

    @staticmethod
    def _find_matching_brace(text: str, open_brace: int) -> int | None:
        depth = 0
        for index in range(open_brace, len(text)):
            char = text[index]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return index
        return None

    @staticmethod
    def _nearest_trace(
        traces: list[SimulinkTrace], statement_offset: int
    ) -> SimulinkTrace | None:
        previous = [trace for trace in traces if trace.offset <= statement_offset]
        if not previous:
            return None
        return max(previous, key=lambda trace: trace.offset)

    @staticmethod
    def _normalize_trace_kind(kind: str) -> str:
        kind = " ".join(kind.split())
        if kind.startswith("Derivatives for "):
            return kind
        if kind.startswith("InitializeConditions for "):
            return kind
        if kind.startswith("Update for "):
            return kind
        return kind

    @staticmethod
    def _extract_referenced_by(comment: str) -> str | None:
        match = re.search(r"Referenced by:\s*'(?P<ref>[^']+)'", comment)
        if match:
            return match.group("ref")
        match = re.search(r":\s*'(?P<ref><[^']+>)'", comment)
        if match:
            return match.group("ref")
        return None

    @staticmethod
    def _extract_expression(comment: str) -> str | None:
        match = re.search(r"Expression:\s*(?P<expr>[^\n*]+)", comment)
        if match:
            return " ".join(match.group("expr").split())
        return None

    @staticmethod
    def _classify_struct(name: str) -> str:
        if name.startswith("ExtU_"):
            return "inputs"
        if name.startswith("ExtY_"):
            return "outputs"
        if name.startswith("B_"):
            return "block_signals"
        if name.startswith("XDot_"):
            return "state_derivatives"
        if name.startswith("XDis_"):
            return "state_disabled"
        if name.startswith("X_"):
            return "continuous_states"
        if name.startswith("DW_") or name.startswith("DWork_"):
            return "dwork_states"
        if name.startswith("P_") or name.endswith("_T_") and name.startswith("P"):
            return "parameters"
        return "unknown"
