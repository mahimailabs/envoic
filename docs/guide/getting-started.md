# Getting Started

## Quick Start

No install needed — run directly:

```bash
uvx envoic scan .
```

## Permanent Install

```bash
# Using uv
uv tool install envoic

# Using pipx
pipx install envoic

# Using pip
pip install envoic
```

## Your First Scan

```bash
# Scan current directory
envoic scan .

# Scan your entire projects folder
envoic scan ~/projects

# Deep scan with size and package info
envoic scan ~/projects --deep

# JSON output for scripting
envoic scan . --json

# Path display mode: name | relative | absolute
envoic scan . --path-mode name
```

## Example Output

```
┌──────────────────────────────────────────────────────────┐
│  ENVOIC - Python Environment Report                      │
│  TR-200  Environment Scanner                             │
├──────────────────────────────────────────────────────────┤
│  Date                               2026-02-09 02:27:39  │
│  Host                                               mac  │
│  Scan Path                           ~/projects          │
│  Scan Depth                                           5  │
│  Duration                                         0.34s  │
├──────────────────────────────────────────────────────────┤
│  Envs Found                                           4  │
│  Total Size                                       2.1G   │
│  Stale >90d                                           1  │
└──────────────────────────────────────────────────────────┘
```
