# Output Formats (JavaScript)

## Default Terminal Report

TR-200 style plain-text report with:
- Header metadata
- `NODE MODULES` table
- `ARTIFACTS` summary table
- Optional size distribution in deep mode

## JSON (`--json`)

Machine-readable output from `scan` including:
- scan metadata
- environments list
- artifacts list
- grouped artifact summary

## List View (`list`)

Compact table for quick inspection without full report wrapper.

## Info View (`info`)

Detailed single-environment report including top package sizes and reinstall hint.
