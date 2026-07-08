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

## Writing docs

Follow the [documentation style guide](STYLE_GUIDE.md) for voice, structure, and formatting conventions.
