from pathlib import Path

from simulink_reconstructor.pipeline import (
    ReconstructionOptions,
    run_reconstruction,
    run_reconstruction_variants,
)


def test_full_pipeline_sample(tmp_path):
    root = Path(__file__).parent / "sample_ccode"
    output = tmp_path / "generated_model_builder.m"

    ir = run_reconstruction(
        ReconstructionOptions(
            input_dir=root,
            output_path=output,
            model_name="reconstructed_model",
        )
    )

    assert output.exists()
    text = output.read_text(encoding="utf-8")
    assert "model = 'reconstructed_model';" in text
    assert "save_system(model);" in text
    assert any(block.block_type == "Gain" for block in ir.blocks)


def test_layout_variant_generation_sample(tmp_path):
    root = Path(__file__).parent / "sample_ccode"

    results = run_reconstruction_variants(input_dir=root, output_dir=tmp_path)

    expected = [
        "generated_model_builder_layout1_hierarchical.m",
        "generated_model_builder_layout2_left_to_right_signal_flow.m",
        "generated_model_builder_layout3_controller_plant_grouped.m",
        "generated_model_builder_layout4_grid_aligned.m",
        "generated_model_builder_layout5_subsystem_modular.m",
        "generated_model_builder_layout6_simple_subsystems.m",
        "generated_model_builder_layout7_complex_subsystems.m",
    ]
    assert len(results) == 7
    for name in expected:
        text = (tmp_path / name).read_text(encoding="utf-8")
        assert "[parsing]" in text
        assert "[summary]" in text
        assert "expectedBlockCount" in text
        assert "save_system(model);" in text
        assert "inferred" in text
