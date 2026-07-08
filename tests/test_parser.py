from pathlib import Path

from simulink_reconstructor.c_parser import CParser
from simulink_reconstructor.loader import CCodeLoader


def parse_sample():
    root = Path(__file__).parent / "sample_ccode"
    return CParser().parse(CCodeLoader(root).load())


def test_function_detection():
    parsed = parse_sample()
    names = {function.name for function in parsed.functions}

    assert "sample_model_step" in names
    assert "sample_model_initialize" in names
    assert "sample_model_terminate" in names
    assert parsed.model_name == "sample_model"


def test_assignment_detection():
    parsed = parse_sample()
    step = parsed.function_by_name("sample_model_step")

    assert step is not None
    assignments = {(item.target, item.expression) for item in step.assignments}
    assert ("sample_model_B.gainOut", "sample_model_P.K * sample_model_U.u") in assignments
    assert ("sample_model_Y.y", "sample_model_B.productOut") in assignments
    assert any(item.trace and item.trace.kind == "Gain" for item in step.assignments)
