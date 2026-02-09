# What is envoic?

envoic is a CLI that finds Python environments across a directory tree and reports what exists, how big it is, and how old it is.

## The problem it solves

Teams accumulate many virtual environments over time:

- old `.venv` folders that are no longer used
- large conda environments consuming disk space
- duplicated project environments spread across many repos
- no quick visibility into stale or abandoned envs

envoic gives you one scan and one report instead of manual guessing.

## How it differs from manual methods

Tools like `which python` answer “what Python is active right now.” They do not discover every environment on disk.

Manual searching (`find`, ad-hoc scripts) can locate directories, but usually misses classification, package metadata, stale detection, and structured output.

envoic combines discovery plus environment-aware detection and reporting in one command.

## TR-200 design philosophy

envoic report output follows a TR-200 terminal style:

- utilitarian and text-first
- information-dense
- predictable layout for humans and screenshots
- no decorative noise

The goal is operational clarity, not visual effects.

## Supported environment types

envoic currently classifies these types:

- `venv` / `virtualenv`
- `conda`
- plain `.env` directories (optional include)
- `unknown` (filtered from normal scan output)
