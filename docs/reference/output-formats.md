# Output Formats

envoic supports three output styles depending on use case.

## 1. Default plain text

The default is a terminal-friendly TR-200 style report with fixed sections:

- header summary
- environments table
- artifacts summary table
- size distribution charts (environments + artifacts)

Best for direct human inspection in terminal sessions.

## 2. JSON (`--json`)

Use JSON for scripting and automation.

```bash
envoic scan . --json
```

Top-level structure includes:

- `scan_path`
- `scan_depth`
- `duration_seconds`
- `environments` (array)
- `artifacts` (array)
- `artifact_summary` (array, grouped by detected pattern)
- `total_size_bytes`
- `hostname`
- `timestamp`

Environment entries include fields like `path`, `env_type`, `python_version`, `size_bytes`, `package_count`, `is_stale`, and `signals`.

Artifact entries include fields like `path`, `category`, `safety`, `size_bytes`, and `pattern_matched`.

## 3. Rich (`--rich`)

If optional `rich` dependency is installed, output can be rendered through Rich.

```bash
envoic scan . --rich
```

If Rich is unavailable, envoic gracefully falls back to plain text output.
