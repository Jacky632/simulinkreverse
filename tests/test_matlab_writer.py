from pathlib import Path

from simulink_reconstructor.c_parser import CParser
from simulink_reconstructor.layout import LayoutEngine
from simulink_reconstructor.loader import CCodeLoader
from simulink_reconstructor.mapper import CToSimulinkMapper
from simulink_reconstructor.matlab_writer import MatlabWriter


def test_matlab_api_command_generation():
    root = Path(__file__).parent / "sample_ccode"
    parsed = CParser().parse(CCodeLoader(root).load())
    ir = CToSimulinkMapper("reconstructed_model").build(parsed)
    LayoutEngine().apply(ir)

    script = MatlabWriter().render(ir)

    assert "new_system(model);" in script
    assert "add_block(" in script
    assert "set_param(" in script
    assert "add_line(model" in script
    assert "save_system(model);" in script
    assert "close_system(model, 0);" in script
