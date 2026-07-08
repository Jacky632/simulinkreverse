"""Command line entry point for Simulink Coder C-to-Simulink reconstruction."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from simulink_reconstructor.pipeline import (
    ReconstructionOptions,
    run_reconstruction,
    run_reconstruction_variants,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Read Simulink Coder generated C from a folder and write a MATLAB "
            "builder script that reconstructs an approximate Simulink model."
        )
    )
    parser.add_argument(
        "--input",
        default="ccode",
        help="Input folder containing generated .c and .h files.",
    )
    parser.add_argument(
        "--output",
        default="generated_model_builder.m",
        help="Output MATLAB script path.",
    )
    parser.add_argument(
        "--model-name",
        default="reconstructed_model",
        help="Name of the model created by the generated MATLAB script.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable progress logging.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable detailed parser and mapping logs.",
    )
    parser.add_argument(
        "--fallback-matlab-functions",
        action="store_true",
        help=(
            "Represent unknown assignments as MATLAB Function fallback blocks "
            "instead of annotations where possible."
        ),
    )
    parser.add_argument(
        "--generate-layout-variants",
        action="store_true",
        help=(
            "Generate the five requested readable-layout MATLAB scripts in the "
            "output directory instead of only one builder script."
        ),
    )
    return parser


def configure_logging(verbose: bool, debug: bool) -> None:
    level = logging.WARNING
    if verbose:
        level = logging.INFO
    if debug:
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format="%(levelname)s:%(name)s:%(message)s",
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args.verbose, args.debug)

    try:
        if args.generate_layout_variants:
            output_dir = Path(args.output).parent
            run_reconstruction_variants(
                input_dir=Path(args.input),
                output_dir=output_dir,
                fallback_matlab_functions=args.fallback_matlab_functions,
                debug=args.debug,
            )
        else:
            options = ReconstructionOptions(
                input_dir=Path(args.input),
                output_path=Path(args.output),
                model_name=args.model_name,
                fallback_matlab_functions=args.fallback_matlab_functions,
                debug=args.debug,
            )
            run_reconstruction(options)
    except Exception as exc:  # pragma: no cover - CLI safety net
        logging.getLogger("simulink_reconstructor").exception("Reconstruction failed")
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
