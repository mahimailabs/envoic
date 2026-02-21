# CLI Commands (JavaScript)

## `envoic scan [PATH]`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--depth` | `-d` | `5` | Maximum directory depth |
| `--deep` |  | `false` | Compute size/package metadata |
| `--json` |  | `false` | Output JSON report |
| `--stale-days` |  | `90` | Days threshold for stale |
| `--no-artifacts` |  | `false` | Disable artifact detection |

## `envoic list [PATH]`

Compact node_modules listing.

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--depth` | `-d` | `5` | Maximum directory depth |
| `--deep` |  | `false` | Compute size metadata |
| `--stale-days` |  | `90` | Days threshold for stale |

## `envoic info <NODE_MODULES_PATH>`

Detailed report for a single `node_modules` directory.

## `envoic manage [PATH]`

Interactive selection and deletion.

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--depth` | `-d` | `5` | Maximum directory depth |
| `--stale-only` |  | `false` | Preselect stale entries |
| `--stale-days` |  | `90` | Days threshold for stale |
| `--dry-run` |  | `false` | Preview only |
| `--yes` | `-y` | `false` | Skip typed confirmation |
| `--deep` |  | `false` | Compute size metadata |

## `envoic clean [PATH]`

Non-interactive stale cleanup.

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--depth` | `-d` | `5` | Maximum directory depth |
| `--stale-days` |  | `90` | Days threshold for stale |
| `--dry-run` |  | `false` | Preview only |
| `--yes` | `-y` | `false` | Skip typed confirmation |
| `--deep` |  | `true` | Compute size metadata |

## `envoic version`

Prints the installed version.
