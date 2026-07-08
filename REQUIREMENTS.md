# Requirements

## Runtime

- Python 3.9 or newer
- MATLAB with Simulink to run the generated `generated_model_builder.m`

The Python runtime code uses only the standard library.

## Development and Tests

- `pytest`

Install test tooling if needed:

```bash
python -m pip install pytest
```

Run tests:

```bash
python -m pytest
```

## Input Assumptions

- The input folder contains Simulink Coder generated `.c` and `.h` files.
- File names are not hard-coded; the tool scans recursively.
- Binary files and common build/report artifacts are ignored.
- The parser is tolerant rather than a full C compiler front end. It is designed
  around common Simulink Coder output patterns and preserves unknown code as
  annotations or fallback blocks.
