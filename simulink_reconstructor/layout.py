"""Deterministic layout variants for reconstructed Simulink diagrams."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from .ir import BlockIR, ModelIR


@dataclass(frozen=True)
class LayoutVariant:
    key: str
    script_name: str
    model_name: str
    title: str
    description: str


LAYOUT_VARIANTS = [
    LayoutVariant(
        key="hierarchical",
        script_name="generated_model_builder_layout1_hierarchical.m",
        model_name="reconstructed_model_layout1_hierarchical",
        title="Hierarchical",
        description=(
            "Rows follow recovered Simulink source hierarchy; dependency depth "
            "still moves signals from left to right within each hierarchy band."
        ),
    ),
    LayoutVariant(
        key="left_to_right_signal_flow",
        script_name="generated_model_builder_layout2_left_to_right_signal_flow.m",
        model_name="reconstructed_model_layout2_left_to_right_signal_flow",
        title="Left-to-right signal flow",
        description=(
            "Blocks are arranged by dependency depth so upstream sources stay "
            "left and downstream outputs move right."
        ),
    ),
    LayoutVariant(
        key="controller_plant_grouped",
        script_name="generated_model_builder_layout3_controller_plant_grouped.m",
        model_name="reconstructed_model_layout3_controller_plant_grouped",
        title="Controller and plant grouped",
        description=(
            "Controller, delay, process/plant, and inferred parameter constants "
            "are separated into readable functional bands."
        ),
    ),
    LayoutVariant(
        key="grid_aligned",
        script_name="generated_model_builder_layout4_grid_aligned.m",
        model_name="reconstructed_model_layout4_grid_aligned",
        title="Grid aligned",
        description=(
            "Blocks are placed on a regular grid by block category and name, "
            "with uniform spacing for scanning and comparison."
        ),
    ),
    LayoutVariant(
        key="subsystem_modular",
        script_name="generated_model_builder_layout5_subsystem_modular.m",
        model_name="reconstructed_model_layout5_subsystem_modular",
        title="Subsystem modular",
        description=(
            "Module-like bands mirror likely subsystem boundaries while keeping "
            "all original inferred logic at the top level for behavior fidelity."
        ),
    ),
    LayoutVariant(
        key="simple_subsystems",
        script_name="generated_model_builder_layout6_simple_subsystems.m",
        model_name="reconstructed_model_layout6_simple_subsystems",
        title="Simple subsystem preferred",
        description=(
            "A compact top-level diagram uses a few coarse subsystems for "
            "controller, plant/process, and inferred parameter helpers."
        ),
    ),
    LayoutVariant(
        key="complex_subsystems",
        script_name="generated_model_builder_layout7_complex_subsystems.m",
        model_name="reconstructed_model_layout7_complex_subsystems",
        title="Complex subsystem preferred",
        description=(
            "A compact top-level diagram uses finer-grained subsystems for "
            "controller, delay, process, condenser, separator, steamjacket, "
            "evaporator, and inferred parameter helpers."
        ),
    ),
]


class LayoutEngine:
    def __init__(
        self,
        strategy: str = "left_to_right_signal_flow",
        x_spacing: int = 190,
        y_spacing: int = 85,
        left: int = 40,
        top: int = 40,
    ) -> None:
        self.strategy = strategy
        self.x_spacing = x_spacing
        self.y_spacing = y_spacing
        self.left = left
        self.top = top

    def apply(self, ir: ModelIR) -> ModelIR:
        if self.strategy == "hierarchical":
            return self._apply_grouped_depth_layout(
                ir,
                group_order=[
                    "I/O",
                    "<Root>",
                    "<S1>",
                    "<S2>",
                    "<S3>",
                    "<S4>",
                    "<S5>",
                    "<S6>",
                    "<S7>",
                    "Inferred",
                    "Other",
                ],
                x_spacing=145,
                y_spacing=56,
                group_spacing=260,
                max_depth_columns=12,
            )
        if self.strategy == "controller_plant_grouped":
            return self._apply_grouped_depth_layout(
                ir,
                group_order=[
                    "I/O",
                    "Controller",
                    "Delay",
                    "Whole Process",
                    "Condenser",
                    "Separator",
                    "Steamjacket",
                    "Evaporator",
                    "Inferred",
                    "Other",
                ],
                x_spacing=145,
                y_spacing=56,
                group_spacing=280,
                grouped_by_function=True,
                max_depth_columns=12,
            )
        if self.strategy == "grid_aligned":
            return self._apply_grid_layout(ir)
        if self.strategy == "subsystem_modular":
            return self._apply_grouped_depth_layout(
                ir,
                group_order=[
                    "I/O",
                    "Root and controller",
                    "Whole Process",
                    "Condenser",
                    "Separator",
                    "Steamjacket",
                    "Evaporator",
                    "Inferred",
                    "Other",
                ],
                x_spacing=145,
                y_spacing=54,
                group_spacing=260,
                grouped_by_module=True,
                max_depth_columns=12,
            )
        if self.strategy in {"simple_subsystems", "complex_subsystems"}:
            return self._apply_grid_layout(ir)
        return self._apply_left_to_right_layout(ir)

    def _apply_left_to_right_layout(self, ir: ModelIR) -> ModelIR:
        depths = self._compute_depths(ir)
        columns: dict[int, list[str]] = defaultdict(list)
        for block in ir.blocks:
            columns[depths.get(block.id, 0)].append(block.id)

        block_by_id = {block.id: block for block in ir.blocks}
        for depth in sorted(columns):
            block_ids = sorted(columns[depth], key=lambda block_id: block_by_id[block_id].name)
            for lane, block_id in enumerate(block_ids):
                block = block_by_id[block_id]
                width, height = self._block_size(block.block_type, block.name)
                x1 = self.left + depth * self.x_spacing
                y1 = self.top + lane * self.y_spacing
                block.position = (x1, y1, x1 + width, y1 + height)
        return ir

    def _apply_grouped_depth_layout(
        self,
        ir: ModelIR,
        group_order: list[str],
        x_spacing: int,
        y_spacing: int,
        group_spacing: int,
        grouped_by_function: bool = False,
        grouped_by_module: bool = False,
        max_depth_columns: int | None = None,
    ) -> ModelIR:
        depths = self._compute_depths(ir)
        grouped_blocks: dict[str, list[BlockIR]] = defaultdict(list)
        for block in ir.blocks:
            if grouped_by_module:
                group = self._module_group(block)
            elif grouped_by_function:
                group = self._functional_group(block)
            else:
                group = self._hierarchy_group(block)
            grouped_blocks[group].append(block)

        unknown_groups = sorted(group for group in grouped_blocks if group not in group_order)
        ordered_groups = [group for group in group_order if group in grouped_blocks] + unknown_groups
        y_cursor = self.top
        for group_index, group in enumerate(ordered_groups):
            blocks = sorted(
                grouped_blocks[group],
                key=lambda block: (depths.get(block.id, 0), block.block_type, block.name),
            )
            if not blocks:
                continue
            min_depth = min(depths.get(block.id, 0) for block in blocks)
            depth_by_block = {
                block.id: max(0, depths.get(block.id, 0) - min_depth) for block in blocks
            }
            if max_depth_columns:
                slot_counts: dict[tuple[int, int], int] = defaultdict(int)
                for block in blocks:
                    depth = depth_by_block[block.id]
                    slot_counts[(depth // max_depth_columns, depth % max_depth_columns)] += 1
                band_heights: dict[int, int] = defaultdict(int)
                for (band, _column), count in slot_counts.items():
                    band_heights[band] = max(band_heights[band], count)
                band_offsets: dict[int, int] = {}
                row_cursor = 0
                for band in sorted(band_heights):
                    band_offsets[band] = row_cursor
                    row_cursor += band_heights[band] + 1
                lanes_by_slot: dict[tuple[int, int], int] = defaultdict(int)
                max_row = 0
                for block in blocks:
                    depth = depth_by_block[block.id]
                    band = depth // max_depth_columns
                    column = depth % max_depth_columns
                    lane = lanes_by_slot[(band, column)]
                    lanes_by_slot[(band, column)] += 1
                    row = band_offsets[band] + lane
                    max_row = max(max_row, row)
                    width, height = self._block_size(block.block_type, block.name)
                    x1 = self.left + 40 + column * x_spacing
                    y1 = y_cursor + 56 + row * y_spacing
                    block.position = (x1, y1, x1 + width, y1 + height)
                y_cursor += max(group_spacing, 110 + (max_row + 1) * y_spacing)
                continue

            lanes_by_depth: dict[int, int] = defaultdict(int)
            max_lane = 0
            for block in blocks:
                depth = depth_by_block[block.id]
                lane = lanes_by_depth[depth]
                lanes_by_depth[depth] += 1
                max_lane = max(max_lane, lane)
                width, height = self._block_size(block.block_type, block.name)
                x1 = self.left + 40 + depth * x_spacing
                y1 = y_cursor + 56 + lane * y_spacing
                block.position = (x1, y1, x1 + width, y1 + height)
            y_cursor += max(group_spacing, 110 + (max_lane + 1) * y_spacing)
        return ir

    def _apply_grid_layout(self, ir: ModelIR) -> ModelIR:
        categories = [
            "Inport",
            "Step",
            "Constant",
            "Gain",
            "Sum",
            "Product",
            "Saturation",
            "Integrator",
            "Discrete-Time Integrator",
            "Unit Delay",
            "Outport",
        ]
        category_index = {name: index for index, name in enumerate(categories)}
        blocks = sorted(
            ir.blocks,
            key=lambda block: (
                category_index.get(block.block_type, len(categories)),
                block.certainty,
                block.name,
            ),
        )
        max_cols = 7
        cell_w = 230
        cell_h = 110
        for index, block in enumerate(blocks):
            col = index % max_cols
            row = index // max_cols
            width, height = self._block_size(block.block_type, block.name)
            x1 = self.left + col * cell_w
            y1 = self.top + row * cell_h
            block.position = (x1, y1, x1 + width, y1 + height)
        return ir

    def _compute_depths(self, ir: ModelIR) -> dict[str, int]:
        incoming: dict[str, list[str]] = defaultdict(list)
        for conn in ir.connections:
            incoming[conn.dst].append(conn.src)

        block_ids = {block.id for block in ir.blocks}
        depths: dict[str, int] = {}

        def depth(block_id: str, visiting: set[str]) -> int:
            if block_id in depths:
                return depths[block_id]
            if block_id in visiting:
                depths[block_id] = 1
                return 1
            visiting.add(block_id)
            sources = [src for src in incoming.get(block_id, []) if src in block_ids]
            if not sources:
                value = 0
            else:
                value = 1 + max(depth(src, visiting) for src in sources)
            visiting.remove(block_id)
            depths[block_id] = value
            return value

        for block in ir.blocks:
            depth(block.id, set())

        max_depth = max(depths.values(), default=0)
        for block in ir.blocks:
            if block.block_type == "Outport":
                depths[block.id] = max_depth + 1
            elif block.block_type == "Inport":
                depths[block.id] = 0
        return depths

    @staticmethod
    def _hierarchy_group(block: BlockIR) -> str:
        if block.certainty == "inferred":
            return "Inferred"
        if block.block_type in {"Inport", "Outport"}:
            return "I/O"
        if block.source_ref:
            if block.source_ref.startswith("<Root>"):
                return "<Root>"
            if block.source_ref.startswith("<S"):
                return block.source_ref.split("/", 1)[0]
        return "Other"

    @staticmethod
    def _functional_group(block: BlockIR) -> str:
        if block.certainty == "inferred":
            return "Inferred"
        if block.block_type in {"Inport", "Outport"}:
            return "I/O"
        ref = block.source_ref or ""
        if ref.startswith("<Root>") or ref.startswith("<S1>"):
            return "Controller"
        if ref.startswith("<S3>"):
            return "Delay"
        if ref.startswith("<S2>"):
            return "Whole Process"
        if ref.startswith("<S4>"):
            return "Condenser"
        if ref.startswith("<S5>"):
            return "Separator"
        if ref.startswith("<S6>"):
            return "Steamjacket"
        if ref.startswith("<S7>"):
            return "Evaporator"
        return "Other"

    @staticmethod
    def _module_group(block: BlockIR) -> str:
        if block.certainty == "inferred":
            return "Inferred"
        if block.block_type in {"Inport", "Outport"}:
            return "I/O"
        ref = block.source_ref or ""
        if ref.startswith("<Root>") or ref.startswith("<S1>") or ref.startswith("<S3>"):
            return "Root and controller"
        if ref.startswith("<S2>"):
            return "Whole Process"
        if ref.startswith("<S4>"):
            return "Condenser"
        if ref.startswith("<S5>"):
            return "Separator"
        if ref.startswith("<S6>"):
            return "Steamjacket"
        if ref.startswith("<S7>"):
            return "Evaporator"
        return "Other"

    @staticmethod
    def _block_size(block_type: str, name: str) -> tuple[int, int]:
        base_width = max(80, min(150, 20 + len(name) * 7))
        if block_type in {"Inport", "Outport"}:
            return (70, 32)
        if block_type in {"Sum", "Product"}:
            return (70, 50)
        if block_type in {"Integrator", "Discrete-Time Integrator", "MATLAB Function"}:
            return (130, 60)
        if block_type == "Saturation":
            return (110, 50)
        return (base_width, 46)
