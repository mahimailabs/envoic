# Reading Reports

A standard report has three sections.

## 1. Header block

Shows scan metadata:

- timestamp
- hostname
- scan path and depth
- scan duration
- total environments and total size
- stale count threshold summary

## 2. Environments table

Each row includes:

- environment path display (name, relative, or absolute)
- Python version
- size (with `--deep`)
- age
- stale marker when applicable

Use `--path-mode` to control path rendering:

- `name` (default): project-oriented short name
- `relative`: relative to scan root
- `absolute`: full path

## 3. Size distribution

A horizontal bar chart compares environment sizes relative to the largest one in the scan.

- full bar = largest environment
- shorter bars = proportional size
- values on the right give exact formatted sizes

## TR-200 philosophy

The TR-200 style is designed for dense terminal reporting:

- fixed-width layout
- legible in logs and screenshots
- no dependency on color
