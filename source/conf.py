import os
import sys
# Prefer local source: add monorepo root (two levels up) if it contains `genesis/`
_local_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
if os.path.isdir(os.path.join(_local_repo_root, "genesis")):
    sys.path.insert(0, _local_repo_root)
import genesis as gs

# We need to initialize Genesis before we can import any of it's classes to document
gs.init(backend=gs.cpu)

__version__ = gs.__version__
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Genesis"
copyright = "2026 Genesis AI SAS"
author = "Genesis Developers"
release = __version__
version = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "myst_parser",
    "sphinx_subfigure",
    "sphinxcontrib.video",
    "sphinx_togglebutton",
    "sphinx_design",
]

# https://myst-parser.readthedocs.io/en/latest/syntax/optional.html
myst_enable_extensions = ["colon_fence", "dollarmath", "amsmath", "dollarmath"]
# https://github.com/executablebooks/MyST-Parser/issues/519#issuecomment-1037239655
myst_heading_anchors = 4

templates_path = ["_templates"]
# exclude_patterns = ["user_guide/reference/_autosummary/*"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_logo = "_static/logo.svg"
html_favicon = "_static/option2_shadow_1.svg"

json_url = "_static/version_switcher.json"
version_match = os.environ.get("READTHEDOCS_VERSION")
if version_match is None:
    version_match = "v" + __version__
html_theme_options = {
    "show_nav_level": 1,
    "use_edit_page_button": True,
    # Footer: only the copyright, matching genesis.ai ("© 2026 Genesis AI SAS").
    # The default theme/Sphinx attribution links are dropped (BSD-2/BSD-3 require
    # retaining the LICENSE notice in the packages, not a rendered footer link).
    "footer_start": ["copyright"],
    "footer_center": [],
    "footer_end": [],
    "logo": {
        "image_dark": "_static/logo_dark.svg",
    },
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/Genesis-Embodied-AI/Genesis",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "Discord",
            "url": "https://discord.gg/nukCuhB47p",
            "icon": "fa-brands fa-discord",
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/genesis-world/",
            "icon": "fa-brands fa-python",
        },
    ],
    "navbar_center": ["version-switcher", "navbar-nav"],
    "show_version_warning_banner": False,
    "switcher": {
        "json_url": json_url,
        "version_match": version_match,
    },
}

html_context = {
    "default_mode": "dark",
    "display_github": True,
    "github_user": "genesis-embodied-ai",
    "github_repo": "genesis-doc",
    "github_version": "main",
    "conf_py_path": "/source/",
    "doc_path": "/source",
}
html_css_files = [
    "css/custom.css",
]
html_static_path = ["_static"]

### Autodoc configurations ###
autodoc_typehints = "signature"
autodoc_typehints_description_target = "all"
autodoc_default_flags = ["members", "show-inheritance", "undoc-members"]
autodoc_member_order = "bysource"
autosummary_generate = True
