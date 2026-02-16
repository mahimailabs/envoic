<p align="center">
  <img src="https://raw.githubusercontent.com/mahimailabs/envoic/main/assets/envoic.png" width="1000" alt="envoic logo" />
</p>

<p align="center">
  <a href="https://coderabbit.ai">
    <img alt="CodeRabbit Pull Request Reviews" src="https://img.shields.io/coderabbit/prs/github/mahimailabs/envoic?utm_source=oss&utm_medium=github&utm_campaign=mahimailabs%2Fenvoic&labelColor=171717&color=FF570A&link=https%3A%2F%2Fcoderabbit.ai&label=CodeRabbit+Reviews" />
  </a>
  <a href="https://pypi.org/project/envoic/">
    <img alt="PyPI version" src="https://img.shields.io/pypi/v/envoic" />
  </a>
  <a href="https://pypi.org/project/envoic/">
    <img alt="Python versions" src="https://img.shields.io/pypi/pyversions/envoic" />
  </a>
  <a href="https://github.com/mahimailabs/envoic/blob/main/LICENSE">
    <img alt="License" src="https://img.shields.io/github/license/mahimailabs/envoic" />
  </a>
  <a href="https://mahimailabs.github.io/envoic/">
    <img alt="Docs" src="https://img.shields.io/badge/docs-GitHub%20Pages-222222?logo=githubpages" />
  </a>
  <a href="https://pepy.tech/projects/envoic">
    <img alt="PyPI Downloads" src="https://static.pepy.tech/personalized-badge/envoic?period=total&units=INTERNATIONAL_SYSTEM&left_color=GREY&right_color=GREEN&left_text=downloads" />
  </a>
</p>

---

Discover Python virtual environments and Python disk artifacts in a compact terminal layout.


> [!WARNING]
> `envoic` is still experimental and therefore subject to major changes across releases. Breaking changes may occur until `v1.0.0`.



# Installation

```bash
$ uv tool install envoic

# or

$ pipx install envoic
```

Run without installing:

```bash
$ uvx envoic scan .
```



# Sample Outputs

## 1. Scan

Scan the current directory for Python virtual environments and artifact directories/files
(`__pycache__`, `.mypy_cache`, `.tox`, `dist/`, `build/`, and more).
Use `--depth` to control recursion and `--deep` to include size metadata.

<img src="https://raw.githubusercontent.com/mahimailabs/envoic/main/assets/scan_sample.png" alt="envoic scan command output" width="900" />

## 2. List

List discovered Python virtual environments in a compact table.

<img src="https://raw.githubusercontent.com/mahimailabs/envoic/main/assets/list_sample.png" alt="envoic list command output" width="900" />

## 3. Info

Get the information about the Python virtual environment in the current directory.

<img src="https://raw.githubusercontent.com/mahimailabs/envoic/main/assets/info_sample.png" alt="envoic info command output" width="900" />

## 4. Manage

Interactively select environments and delete the selected ones with confirmation.

<img src="https://raw.githubusercontent.com/mahimailabs/envoic/main/assets/manage_sample.png" alt="envoic manage command output" width="900" />

## 5. Clean

Delete stale environments in batch mode (supports `--dry-run` and confirmation).

<img src="https://raw.githubusercontent.com/mahimailabs/envoic/main/assets/clean_sample.png" alt="envoic clean command output" width="900" />

## Usage

```bash
$ envoic scan [PATH]
$ envoic scan ~/projects --deep
$ envoic scan ~/projects --no-artifacts

$ envoic list [PATH]

$ envoic manage [PATH]

$ envoic clean [PATH]

$ envoic info <ENV_PATH>

$ envoic version
```

Read more at [Documentation](https://mahimailabs.github.io/envoic/)


## Local Development

```bash
$ uv sync --group dev

$ uv run pytest

$ uv run python -m envoic.cli scan . --deep --path-mode name
```

## License

[MIT](https://github.com/mahimailabs/envoic/blob/main/LICENSE)
