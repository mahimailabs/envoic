<p align="center">
  <img src="https://raw.githubusercontent.com/mahimailabs/envoic/main/assets/envoic.png" width="1000" alt="envoic logo" />
</p>

Discover and manage development environments across Python and JavaScript.

## Python

Find scattered `.venv` directories, Python caches, build artifacts, and more.

```bash
uvx envoic scan ~/projects
```

[Python package →](./packages/python/)

## JavaScript

Find `node_modules`, build caches, and JavaScript artifacts.

```bash
npx envoic scan ~/projects
```

[JavaScript package →](./packages/js/)

## Install

No install needed:

```bash
uvx envoic scan .
npx envoic scan .
```

Install permanently:

```bash
uv tool install envoic      # Python
npm install -g envoic       # JavaScript
```

## Agent Skill

envoic is available as an [Agent Skill](https://agentskills.io) for coding agents:

| Tool | Auto-detected file | Notes |
|---|---|---|
| Cursor | `.cursorrules` | Generated from `skills/envoic/templates/cursor.cursorrules` |
| GitHub Copilot | `.github/copilot-instructions.md` | Generated from `skills/envoic/templates/copilot-instructions.md` |
| OpenAI Codex | `.agents/skills/envoic/SKILL.md` | Symlink/copy of canonical skill |
| Claude Code | `.claude-plugin/plugins.yaml` | Generated from `skills/envoic/templates/claude-plugins.yaml` |

Install from marketplace in Claude Code:

    /plugin marketplace add mahimailabs/envoic

Canonical skill source:

```text
skills/envoic/
  SKILL.md
  agents/openai.yaml
  references/
  templates/
```

Sync generated adapter files after skill updates:

```bash
python3 scripts/sync-agent-instructions.py
```

If your environment does not support symlinks, copy `skills/envoic/` into `.agents/skills/envoic/`.

## Docs

- Site: https://mahimailabs.github.io/envoic/
- Contributing: [CONTRIBUTING.md](./CONTRIBUTING.md)
- Code of Conduct: [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)

## License

[MIT](./LICENSE)
