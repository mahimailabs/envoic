# Configuration

envoic is currently CLI-first and has no config file.

## Scan command options

- `--depth`, `-d` (default: `5`)
- `--deep` (default: `false`)
- `--json` (default: `false`)
- `--stale-days` (default: `90`)
- `--include-dotenv` (default: `false`)
- `--path-mode` (default: `name`; options: `name`, `relative`, `absolute`)
- `--rich` (default: `false`)

## List command options

- `--depth`, `-d` (default: `5`)
- `--deep` (default: `false`)
- `--stale-days` (default: `90`)
- `--include-dotenv` (default: `false`)
- `--path-mode` (default: `name`; options: `name`, `relative`, `absolute`)
- `--rich` (default: `false`)

## Manage command options

- `--depth`, `-d` (default: `5`)
- `--stale-only` (default: `false`)
- `--stale-days` (default: `90`)
- `--dry-run` (default: `false`)
- `--yes`, `-y` (default: `false`)
- `--deep` (default: `false`)

## Clean command options

- `--depth`, `-d` (default: `5`)
- `--stale-days` (default: `90`)
- `--dry-run` (default: `false`)
- `--yes`, `-y` (default: `false`)
- `--deep` / `--no-deep` (default: `true`)

## Future direction

Potential future enhancement:

- project-level config file for default scan depth, stale threshold, and output mode
