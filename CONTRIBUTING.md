# Contributing

Thanks for considering contributing!

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
pytest
```

## Pull requests

- Keep PRs small and focused.
- Add or update tests where applicable.
- Update documentation if you change public behavior.
- Run `pytest` and `ruff` before submitting.

## Reporting issues

Please include:
- OS and Python version
- `rail-ifc-quality-gate --version`
- A minimal reproduction (ideally using `examples/toy_ifc_generated`)
