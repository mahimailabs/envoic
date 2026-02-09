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
