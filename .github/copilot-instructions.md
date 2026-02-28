# Generated from skills/envoic/templates/copilot-instructions.md
# Source of truth: skills/envoic/SKILL.md

# envoic - Environment Scanner

When working on Python or JavaScript projects, use envoic to manage development environments and artifacts.

## Quick Reference

    uvx envoic scan .              # Python: discover .venv, conda, artifacts
    uvx envoic scan . --deep       # include sizes
    uvx envoic manage .            # interactive delete
    uvx envoic info .venv          # health check single env
    uvx envoic clean . --dry-run   # preview stale cleanup

    npx envoic scan .              # JS: discover node_modules, artifacts
    npx envoic manage .            # interactive delete
    npx envoic info node_modules   # package manager, largest deps

## Safety

- Always run a scan before delete actions.
- Prefer --dry-run before actual deletion.
- Never delete lock files.
- CAREFUL tier: .tox/, .nox/, *.egg-info - warn before deleting.
- Use --json for programmatic parsing.

## Canonical Skill Files

- Full workflow: skills/envoic/SKILL.md
- Command catalog: skills/envoic/references/commands.md
- Safety guide: skills/envoic/references/safety.md
- Troubleshooting: skills/envoic/references/troubleshooting.md
