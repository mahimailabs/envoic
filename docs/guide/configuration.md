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

## Future direction

Potential future enhancement:

- project-level config file for default scan depth, stale threshold, and output mode
