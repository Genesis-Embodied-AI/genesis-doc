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

Before contributing, always read the [documentation style guide](STYLE_GUIDE.md). It defines the voice, structure, and formatting conventions every page follows; bring any page you touch in line with it.

## Questions, requests, and bugs

This repository holds the documentation only. For anything about Genesis World itself, use the main repository:

- **Feature discussions and questions:** [genesis-world discussions](https://github.com/Genesis-Embodied-AI/genesis-world/discussions).
- **Feature requests and bug reports:** [genesis-world issues](https://github.com/Genesis-Embodied-AI/genesis-world/issues).

## Publishing

The site is built and hosted by [Read the Docs](https://readthedocs.org/). The `genesis-world` repository includes this repository as a Git submodule, so a documentation change does not appear on the published site until the submodule pointer in `genesis-world` is updated to the new commit. After your changes merge here, bump that submodule reference in `genesis-world`.
