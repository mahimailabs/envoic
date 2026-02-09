# envoic

`envoic` is a fast, opinionated CLI that discovers Python virtual environments and reports them in a clean, information-dense terminal layout.

## Quick Start

No install needed:

```bash
uvx envoic scan ~/projects
```

Or install permanently:

```bash
uv tool install envoic
# or
pipx install envoic
```

## Commands

```bash
envoic scan [PATH]
envoic list [PATH]
envoic info <ENV_PATH>
envoic version
```

### `scan`

```bash
envoic scan . --depth 5
envoic scan ~/projects --deep
envoic scan . --json
envoic scan . --include-dotenv
envoic scan . --rich
```

Options:

- `--depth`, `-d`: max scan depth (default: `5`)
- `--deep`: compute size and package metadata
- `--json`: output JSON
- `--stale-days`: stale threshold in days (default: `90`)
- `--include-dotenv`: include plain `.env` directories
- `--rich`: optional rich-rendered output

### `list`

Compact table-only output:

```bash
envoic list .
```

### `info`

Detailed report for one environment:

```bash
envoic info .venv
```

## Development

```bash
uv sync --group dev
uv run pytest
uvx --from . envoic scan .
```

## License

BSD-3-Clause
