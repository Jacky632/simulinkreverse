"""End-to-end reconstruction pipeline."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path

from .c_parser import CParser
from .layout import LAYOUT_VARIANTS, LayoutEngine
from .loader import CCodeLoader
from .mapper import CToSimulinkMapper
from .matlab_writer import MatlabWriter

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ReconstructionOptions:
    input_dir: Path
    output_path: Path
    model_name: str
    fallback_matlab_functions: bool = False
    debug: bool = False
    layout_strategy: str = "left_to_right_signal_flow"
    layout_title: str = "Left-to-right signal flow"
    layout_description: str = (
        "Blocks are arranged by dependency depth so upstream sources stay left "
        "and downstream outputs move right."
    )


def run_reconstruction(options: ReconstructionOptions):
    LOGGER.info("Scanning C code folder: %s", options.input_dir)
    source_files = CCodeLoader(options.input_dir).load()
    LOGGER.info("Loaded %d C/header files", len(source_files))

    parsed = CParser().parse(source_files)
    LOGGER.info("Detected %d functions", len(parsed.functions))
    LOGGER.info("Detected %d structs", len(parsed.structs))
    LOGGER.info("Detected %d parameters", len(parsed.parameters))

    mapper = CToSimulinkMapper(
        model_name=options.model_name,
        fallback_matlab_functions=options.fallback_matlab_functions,
    )
    ir = mapper.build(parsed)
    LOGGER.info("Inferred %d blocks", len(ir.blocks))
    LOGGER.info("Inferred %d connections", len(ir.connections))

    ir.metadata["layout_strategy"] = options.layout_title
    ir.metadata["layout_key"] = options.layout_strategy
    ir.metadata["layout_description"] = options.layout_description
    LOGGER.info("Applying layout strategy: %s", options.layout_title)
    LayoutEngine(strategy=options.layout_strategy).apply(ir)
    MatlabWriter().write(ir, options.output_path)
    LOGGER.info("Output path: %s", options.output_path)
    return ir


def run_reconstruction_variants(
    input_dir: Path,
    output_dir: Path,
    fallback_matlab_functions: bool = False,
    debug: bool = False,
):
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for variant in LAYOUT_VARIANTS:
        LOGGER.info("Generating layout variant: %s", variant.title)
        options = ReconstructionOptions(
            input_dir=input_dir,
            output_path=output_dir / variant.script_name,
            model_name=variant.model_name,
            fallback_matlab_functions=fallback_matlab_functions,
            debug=debug,
            layout_strategy=variant.key,
            layout_title=variant.title,
            layout_description=variant.description,
        )
        results.append(run_reconstruction(options))
    return results
