# CLI Commands

## `envoic scan [PATH]`

Scans a path for Python environments and prints the full TR-200 report.

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--depth` | `-d` | `5` | Maximum directory depth to scan |
| `--deep` |  | `false` | Compute size and package metadata |
| `--json` |  | `false` | Output JSON report |
| `--stale-days` |  | `90` | Days threshold for stale marking |
| `--include-dotenv` |  | `false` | Include plain `.env` directories |
| `--path-mode` |  | `name` | Path column rendering: `name`, `relative`, `absolute` |
| `--rich` |  | `false` | Use rich-rendered output |

Examples:

```bash
envoic scan .
envoic scan ~/projects --deep
envoic scan . --json
envoic scan . --path-mode relative
```

## `envoic list [PATH]`

Prints a compact environments table without the full report wrapper.

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--depth` | `-d` | `5` | Maximum directory depth to scan |
| `--deep` |  | `false` | Compute size and package metadata |
| `--stale-days` |  | `90` | Days threshold for stale marking |
| `--include-dotenv` |  | `false` | Include plain `.env` directories |
| `--path-mode` |  | `name` | Path column rendering: `name`, `relative`, `absolute` |
| `--rich` |  | `false` | Use rich-rendered output |

## `envoic info <ENV_PATH>`

Shows detailed information for one environment.

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--rich` |  | `false` | Use rich-rendered output |

## `envoic version`

Prints the installed envoic version.
