# Detection Logic (JavaScript)

## `node_modules` Detection

Definitive signals:
- `node_modules/.package-lock.json` (npm)
- `node_modules/.yarn-integrity` (yarn classic)
- `node_modules/.modules.yaml` (pnpm)

Strong signal:
- Parent directory contains `package.json`

## Package Manager Classification

Priority order checks lockfiles and internal marker files for:
- `pnpm`
- `yarn`
- `bun`
- `npm`
- fallback: `unknown`

## Freshness Signals

- `isStale`: `node_modules` modified older than `--stale-days`
- `isOutdated`: parent `package.json` modified after `node_modules`

## Artifact Detection

Artifacts are matched by known names/patterns and grouped by safety level:
- `always_safe`
- `usually_safe`
- `careful`
