"""Deterministic layout for reconstructed Simulink diagrams."""

from __future__ import annotations

from collections import defaultdict

from .ir import ModelIR


class LayoutEngine:
    def __init__(
        self,
        x_spacing: int = 190,
        y_spacing: int = 85,
        left: int = 40,
        top: int = 40,
    ) -> None:
        self.x_spacing = x_spacing
        self.y_spacing = y_spacing
        self.left = left
        self.top = top

    def apply(self, ir: ModelIR) -> ModelIR:
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
