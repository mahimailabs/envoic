# Detection Logic

envoic classifies directories by combining definitive and strong filesystem signals.

## Signal hierarchy

### Definitive signals

- `pyvenv.cfg` present

This is the strongest indicator for `venv`/`virtualenv` style environments.

### Strong signals

- Python executable (`bin/python` or `Scripts/python.exe`)
- site-packages directory layout
- activate scripts
- `conda-meta` directory

Multiple strong signals increase confidence.

## Classification rules

At a high level:

1. If `conda-meta` exists → classify as `conda`.
2. Else if definitive/strong venv signals match → classify as `venv`.
3. Else if directory name is `.env` → classify as `dotenv_dir`.
4. Else → `unknown`.

Normal scan output excludes `unknown`.

## Signals field

Each detected environment carries a `signals` list that records matched checks, such as:

- `pyvenv.cfg`
- `conda-meta`
- `python-binary`
- `site-packages`
- `python+site-packages`
- `activate-script`

This makes detection decisions inspectable and scriptable.

## Artifact detection

The scanner also detects Python ecosystem artifacts during the same filesystem walk:

- Bytecode: `__pycache__/`, `*.pyc`, `*.pyo`
- Tool caches: `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`
- Test envs: `.tox/`, `.nox/`
- Build artifacts: `dist/`, `build/`, `.eggs/`, `*.egg-info/`
- Coverage/notebook: `.ipynb_checkpoints/`, `htmlcov/`, `.coverage`

Safety tiers are reported per pattern:

- `always_safe`: regenerated automatically
- `usually_safe`: usually fine to remove, may require rebuild
- `careful`: may break editable installs or take time to recreate

`build/` and `dist/` are only treated as Python artifacts when their parent directory
looks like a Python project (`pyproject.toml`, `setup.py`, or `setup.cfg` present).
