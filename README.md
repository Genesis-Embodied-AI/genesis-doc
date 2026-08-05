# Genesis World Documentation

Source for the Genesis World documentation site, built with [Sphinx](https://www.sphinx-doc.org/) and [MyST Markdown](https://myst-parser.readthedocs.io/).

## Building locally

1. Create a clean Python environment (Python ≥ 3.10) and install Genesis World together with the docs dependencies:

   ```bash
   pip install genesis-world
   pip install -r requirements.txt
   ```

2. Build the site and rebuild it on every change:

   ```bash
   make html
   sphinx-autobuild ./source ./build/html
   ```

   The rendered docs are then served at http://127.0.0.1:8000.

## Contributing

Before contributing, read both guides and bring any page you touch in line with them:

- [Style guide](STYLE_GUIDE.md): what belongs on a page, how it is structured, and how it is marked up.
- [Voice guide](VOICE.md): how the sentences read, the patterns we avoid, and the register these pages use.

## Questions, requests, and bugs

This repository holds the documentation only. For anything about Genesis World itself, use the main repository:

- **Feature discussions and questions:** [genesis-world discussions](https://github.com/Genesis-Embodied-AI/genesis-world/discussions).
- **Feature requests and bug reports:** [genesis-world issues](https://github.com/Genesis-Embodied-AI/genesis-world/issues).

## Publishing

The site is built and hosted by [Read the Docs](https://readthedocs.org/). The `genesis-world` repository includes this repository as a Git submodule, so a documentation change does not appear on the published site until the submodule pointer in `genesis-world` is updated to the new commit. After your changes merge here, bump that submodule reference in `genesis-world`.
