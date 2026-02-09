# Scanning Environments

## Depth control

Use `--depth` (or `-d`) to limit recursion depth.

```bash
envoic scan ~/projects --depth 3
```

Lower values scan faster and avoid broad filesystem walks.

`--depth` controls *where* envoic looks.
`--deep` controls *how much metadata* envoic collects for each found environment.

## Skipped directories

Scanner traversal skips known noisy directories:

- `node_modules`
- `.git`
- `__pycache__`
- other hidden directories except selected environment-related names

This keeps scans focused and efficient.

## Deep mode

Use `--deep` to collect extra metadata:

- total environment size (`size_bytes`)
- package count from site-packages metadata
- more complete version extraction

Deep mode is slower because it walks files and inspects package metadata.

## Stale detection

Use `--stale-days` to mark environments stale based on modified time.

```bash
envoic scan . --stale-days 120
```

Default is `90` days.

## Include plain `.env` directories

By default, plain `.env` directories are excluded unless strong Python signals are present.

Use `--include-dotenv` to include these directories explicitly.
