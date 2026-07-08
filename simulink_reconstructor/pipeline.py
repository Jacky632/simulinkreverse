"""End-to-end reconstruction pipeline."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path

from .c_parser import CParser
from .layout import LayoutEngine
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

    LayoutEngine().apply(ir)
    MatlabWriter().write(ir, options.output_path)
    LOGGER.info("Output path: %s", options.output_path)
    return ir
