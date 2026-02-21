# Managing (JavaScript)

Use `manage` for interactive deletion and `clean` for stale-only cleanup.

## Interactive Cleanup

```bash
envoic manage ~/projects --deep
```

Flow:
1. Scan environments.
2. Select targets in checkbox UI (or numbered fallback in non-TTY).
3. Review summary.
4. Type `delete` to confirm.

## Stale-Only Cleanup

```bash
# Preview
envoic clean ~/projects --dry-run

# Delete stale node_modules with confirmation
envoic clean ~/projects --stale-days 90

# Skip final prompt (automation)
envoic clean ~/projects --yes
```

## Safety Rules

- Requires explicit confirmation by default (`delete`).
- Deletes only selected directories.
- Symlinks are unlinked without deleting targets.
- Rejects paths outside scan root.
