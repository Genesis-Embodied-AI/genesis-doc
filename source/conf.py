import os
import sys
# 优先使用本地源码：如果上级目录包含 `genesis/`，则将其加入路径
_local_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
if os.path.isdir(os.path.join(_local_repo_root, "genesis")):
    sys.path.insert(0, _local_repo_root)
import genesis as gs

# 我们需要在导入任何 Genesis 类进行文档化之前先初始化 Genesis
gs.init(backend=gs.cpu)

__version__ = gs.__version__
# Sphinx 文档构建器的配置文件。
#
# 有关内置配置值的完整列表，请参阅文档：
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- 项目信息 -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Genesis"
copyright = "2024, Genesis Developers"
author = "Genesis Developers"
release = __version__
version = __version__

# -- 通用配置 ---------------------------------------------------
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


# -- HTML 输出选项 -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_logo = "_static/bigger_text.png"
html_favicon = "_static/option2_shadow_1.svg"

json_url = "_static/version_switcher.json"
version_match = os.environ.get("READTHEDOCS_VERSION")
if version_match is None:
    version_match = "v" + __version__
html_theme_options = {
    "show_nav_level": 2,
    "use_edit_page_button": True,
    "logo": {
        "image_dark": "_static/bigger_text_white.png",
    },
    "navbar_center": ["version-switcher", "navbar-nav"],
    "show_version_warning_banner": False,
    "switcher": {
        "json_url": json_url,
        "version_match": version_match,
    },
}

html_context = {
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

### Autodoc 配置 ###
autodoc_typehints = "signature"
autodoc_typehints_description_target = "all"
autodoc_default_flags = ["members", "show-inheritance", "undoc-members"]
autodoc_member_order = "bysource"
autosummary_generate = True
