# Contributing to envoic

Thank you for your interest in contributing to `envoic`! This guide will get you started quickly.

## Development Setup

1. Fork and clone the repository.
2. Install dependencies:

```bash
uv sync --group dev
```

3. Run checks before opening a PR:

```bash
uv run pytest
uv run mypy src tests
uv run ruff check .
```

4. (Optional) Build docs locally:

```bash
cd docs
npm ci
npm run build
```

## Project Structure

- `src/envoic/cli.py`: CLI commands and wiring
- `src/envoic/scanner.py`: filesystem traversal/discovery
- `src/envoic/detector.py`: environment detection/classification
- `src/envoic/report.py`: terminal output formatting
- `src/envoic/manager.py`: interactive cleanup workflows
- `tests/`: unit tests
- `docs/`: VitePress documentation

## Contribution Guidelines

- Keep changes focused and small.
- Add or update tests for behavior changes.
- Keep CLI help and docs aligned with code changes.
- Prefer explicit, safe behavior for destructive actions.
- Avoid breaking changes unless discussed in an issue first.

## Pull Request Checklist

- [ ] Tests pass locally (`uv run pytest`)
- [ ] Type checks pass (`uv run mypy src tests`)
- [ ] Lint passes (`uv run ruff check .`)
- [ ] Docs updated (if command behavior changed)
- [ ] PR description explains what changed and why

## Commit Message Style

Use clear, imperative commit messages. Examples:

- `add clean command dry-run summary`
- `fix manage selector path formatting`
- `update docs for path-mode behavior`

## Reporting Bugs / Requesting Features

Open an issue with:

- expected behavior
- actual behavior
- reproduction steps
- environment details (OS, Python version, envoic version)

## Questions

If you are unsure where to start, open an issue labeled question and ask for a beginner-friendly starting point.
