# Configuration

envoic is currently CLI-first and has no config file.

## Scan command options

- `--depth`, `-d` (default: `5`)
- `--deep` (default: `false`)
- `--json` (default: `false`)
- `--stale-days` (default: `90`)
- `--include-dotenv` (default: `false`)
- `--artifacts` / `--no-artifacts` (default: `--artifacts`)
- `--show-artifacts`, `-a` (default: `false`)
- `--path-mode` (default: `name`; options: `name`, `relative`, `absolute`)
- `--rich` (default: `false`)

Artifact detection is enabled by default for `scan`. Use `--no-artifacts` when
you only want Python environments in the report. Use `--show-artifacts` to show
the detailed artifact rows instead of the default summary placeholder.

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
