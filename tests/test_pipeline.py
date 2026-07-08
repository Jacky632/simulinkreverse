from pathlib import Path

from simulink_reconstructor.pipeline import ReconstructionOptions, run_reconstruction


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
