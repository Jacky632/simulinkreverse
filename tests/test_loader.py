from pathlib import Path

from simulink_reconstructor.loader import CCodeLoader


def test_loader_finds_c_and_h_and_ignores_artifacts():
    root = Path(__file__).parent / "sample_ccode"
    files = CCodeLoader(root).load()
    rels = {file.relative_path for file in files}

    assert "sample_model.c" in rels
    assert "sample_model.h" in rels
    assert "ignored.o" not in rels
