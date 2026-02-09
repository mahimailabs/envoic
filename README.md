<img src="assets/envoic.png" width="500" />

---

Discover Python virtual environments and report them in a compact terminal layout.


> [!WARNING]
> `envoic` is still experimental and therefore subject to major changes across releases. Breaking changes may occur until `v1.0.0`.


- Docs: https://mahimailabs.github.io/envoic/
- PyPI: https://pypi.org/project/envoic/

## Install

```bash
uv tool install envoic
# or
pipx install envoic
```

Run without installing:

```bash
uvx envoic scan .
```

## Usage

```bash
envoic scan [PATH]
envoic list [PATH]
envoic info <ENV_PATH>
envoic version
```

Common examples:

```bash
envoic scan . --deep
envoic scan . --json
envoic scan . --path-mode name      # name | relative | absolute
envoic list . --path-mode relative
envoic info .venv
```

## Local Development

```bash
uv sync --group dev
uv run pytest
uv run python -m envoic.cli scan . --deep --path-mode name
```

## License

BSD-3-Clause
