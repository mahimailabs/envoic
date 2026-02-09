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

![Scan command output](/scan_sample.png)

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

![List command output](/list_sample.png)

## `envoic manage [PATH]`

Interactively select and delete environments.

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--depth` | `-d` | `5` | Maximum directory depth to scan |
| `--stale-only` |  | `false` | Pre-select stale environments in selector |
| `--stale-days` |  | `90` | Days threshold for stale marking |
| `--dry-run` |  | `false` | Preview deletions without deleting |
| `--yes` | `-y` | `false` | Skip typed confirmation (dangerous) |
| `--deep` |  | `false` | Compute size and package metadata for selection view |

![Manage command output](/manage_sample.png)

## `envoic clean [PATH]`

Delete stale environments without interactive selection.

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--depth` | `-d` | `5` | Maximum directory depth to scan |
| `--stale-days` |  | `90` | Delete environments older than N days |
| `--dry-run` |  | `false` | Preview deletions without deleting |
| `--yes` | `-y` | `false` | Skip typed confirmation (dangerous) |
| `--deep` |  | `true` | Compute size metadata for stale candidates |

![Clean command output](/clean_sample.png)

## `envoic info <ENV_PATH>`

Shows detailed information for one environment.

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--rich` |  | `false` | Use rich-rendered output |

![Info command output](/info_sample.png)

## `envoic version`

```bash
❯ uvx envoic version
0.0.4
```

Prints the installed envoic version.
