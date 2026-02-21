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

## Docs

- Site: https://mahimailabs.github.io/envoic/
- Contributing: [CONTRIBUTING.md](./CONTRIBUTING.md)
- Code of Conduct: [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)

## License

[MIT](./LICENSE)
