# Getting Started (JavaScript)

`envoic` also ships as an npm CLI for Node.js projects.

## Quick Start

```bash
npx envoic scan .
```

## Install

```bash
npm install -g envoic
```

## Common Commands

```bash
# Full report
envoic scan ~/projects

# Deep scan with size metadata
envoic scan ~/projects --deep

# Compact listing
envoic list ~/projects

# Inspect one project's node_modules
envoic info ~/projects/my-app/node_modules
```

## Next

- [Scanning (JS)](/guide/js-scanning)
- [Managing (JS)](/guide/js-managing)
- [CLI Commands (JS)](/reference/js-commands)
