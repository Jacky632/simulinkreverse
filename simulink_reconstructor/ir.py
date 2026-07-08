"""Intermediate representation independent of MATLAB syntax."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SignalIR:
    name: str
    role: str
    data_type: str | None = None
    source_ref: str | None = None
    certainty: str = "certain"


@dataclass
class ParameterIR:
    name: str
    value: str | None = None
    expression: str | None = None
    source_ref: str | None = None
    certainty: str = "certain"


@dataclass
class BlockIR:
    id: str
    name: str
    block_type: str
    output: str | None = None
    inputs: list[str] = field(default_factory=list)
    parameters: dict[str, str] = field(default_factory=dict)
    source_ref: str | None = None
    source_function: str | None = None
    source_line: int | None = None
    expression: str | None = None
    unmapped_code: str | None = None
    certainty: str = "inferred"
    execution_index: int = 0
    position: tuple[int, int, int, int] | None = None


@dataclass(frozen=True)
class ConnectionIR:
    src: str
    dst: str
    src_port: int = 1
    dst_port: int = 1
    signal: str | None = None
    inferred: bool = True
    reason: str | None = None


@dataclass
class ModelIR:
    model_name: str
    original_model_name: str | None = None
    inputs: list[SignalIR] = field(default_factory=list)
    outputs: list[SignalIR] = field(default_factory=list)
    signals: list[SignalIR] = field(default_factory=list)
    parameters: list[ParameterIR] = field(default_factory=list)
    states: list[SignalIR] = field(default_factory=list)
    blocks: list[BlockIR] = field(default_factory=list)
    connections: list[ConnectionIR] = field(default_factory=list)
    annotations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)
