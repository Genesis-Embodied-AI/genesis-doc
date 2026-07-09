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

project = "Genesis World"
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
# The navbar brand is the text "Genesis World" (html_theme_options["logo"]["text"]),
# not an image; the logo mark now lives in the footer (see footer-logo component).
# html_title also fixes the browser-tab title to "Genesis World" rather than the
# default "Genesis World <version> documentation".
html_title = "Genesis World"
# Baseline favicon is the multi-resolution .ico (understood everywhere); the
# adaptive SVG and apple-touch-icon are added in setup() below so modern
# browsers prefer the crisp, theme-aware SVG.
html_favicon = "_static/favicon.ico"

json_url = "_static/version_switcher.json"
version_match = os.environ.get("READTHEDOCS_VERSION")
if version_match is None:
    version_match = "v" + __version__
html_theme_options = {
    "show_nav_level": 1,
    "use_edit_page_button": True,
    # Footer: the Genesis company logo on the left, copyright on the right
    # (matching genesis.ai, "© 2026 Genesis AI SAS"). The default theme/Sphinx
    # attribution links are dropped (BSD-2/BSD-3 require retaining the LICENSE
    # notice in the packages, not a rendered footer link).
    "footer_start": ["footer-logo"],
    "footer_center": [],
    "footer_end": ["copyright"],
    # Navbar brand is the text "Genesis World" (no image).
    "logo": {
        "text": "Genesis World",
    },
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/Genesis-Embodied-AI/genesis-world",
            "icon": "fa-brands fa-github",
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

def _add_favicon_links(app, pagename, templatename, context, doctree):
    # Supplement the .ico (set via html_favicon) with the theme-adaptive SVG and
    # an apple-touch-icon. Browsers that support SVG favicons prefer the SVG.
    pathto = context.get("pathto")
    if pathto is None:
        return
    links = (
        f'<link rel="icon" type="image/svg+xml" href="{pathto("_static/favicon.svg", 1)}">'
        f'<link rel="apple-touch-icon" href="{pathto("_static/apple-touch-icon.png", 1)}">'
    )
    context["metatags"] = context.get("metatags", "") + links


def _clean_pydantic_signatures(app, what, name, obj, options, signature, return_annotation):
    # Pydantic models keep the Annotated[...] validator metadata in their field
    # annotations, which autodoc renders as unreadable
    # `tuple[typing.Annotated[..., FieldInfo(...)]]` blobs in the class signature.
    # Recompute the signature: sphinx's stringify_signature drops the Annotated
    # extras, leaving clean, readable type hints (e.g. `tuple[float, ...] | float`).
    import pydantic
    from sphinx.util.inspect import signature as sphinx_signature, stringify_signature

    if what != "class" or not isinstance(obj, type) or not issubclass(obj, pydantic.BaseModel):
        return None
    try:
        cleaned = stringify_signature(sphinx_signature(obj))
    except Exception:
        return None
    return cleaned, return_annotation


def setup(app):
    app.connect("html-page-context", _add_favicon_links)
    app.connect("autodoc-process-signature", _clean_pydantic_signatures)


### Autodoc configurations ###
autodoc_typehints = "signature"
autodoc_typehints_description_target = "all"
autodoc_default_flags = ["members", "show-inheritance", "undoc-members"]
autodoc_member_order = "bysource"
autosummary_generate = True
