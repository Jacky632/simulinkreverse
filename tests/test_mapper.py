from pathlib import Path

from simulink_reconstructor.c_parser import CParser
from simulink_reconstructor.loader import CCodeLoader
from simulink_reconstructor.mapper import CToSimulinkMapper


def build_ir():
    root = Path(__file__).parent / "sample_ccode"
    parsed = CParser().parse(CCodeLoader(root).load())
    return CToSimulinkMapper("reconstructed_model").build(parsed)


def test_simple_expression_mapping_to_blocks():
    ir = build_ir()
    block_types = {block.block_type for block in ir.blocks}

    assert "Gain" in block_types
    assert "Sum" in block_types
    assert "Product" in block_types
    assert "Constant" in block_types
    assert "Unit Delay" in block_types


def test_connections_are_inferred():
    ir = build_ir()

    assert ir.connections
    assert any(conn.signal == "signal:gainOut" for conn in ir.connections)
    assert any(conn.signal == "input:u" for conn in ir.connections)
