# Scanning (JavaScript)

`envoic` scans for JavaScript environments and generated artifacts.

## What It Detects

- `node_modules` environments
- Build/tool artifacts such as `.next`, `.turbo`, `dist`, `build`, `.cache`, `coverage`

## Key Flags

```bash
# Set max depth
envoic scan ~/projects --depth 6

# Compute size and package metadata
envoic scan ~/projects --deep

# JSON output
envoic scan ~/projects --json

# Stale threshold
envoic scan ~/projects --stale-days 120

# Disable artifact detection
envoic scan ~/projects --no-artifacts
```

## Stale vs Outdated

- `STALE`: `node_modules` is older than `--stale-days`.
- `OUTDATED`: `package.json` is newer than `node_modules`.
