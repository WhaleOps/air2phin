# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import base64
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join("..", "src")))

from airphin import __version__  # noqa

project = "airphin"
copyright = "2022, Jay Chung"
author = "Jay Chung"
release = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # Measures durations of Sphinx processing
    "sphinx.ext.duration",
    "sphinx.ext.autosectionlabel",
    "sphinx_copybutton",
    # argparse
    "sphinxarg.ext",
    # changelog
    "sphinx_github_changelog",
]

# -- Extensions configuration -------------------------------------------------
# autosectionlabel
autosectionlabel_prefix_document = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# extensions for sphinx_github_changelog, token from Jay Chung with None permission scope. have to encode it
# due to github will delete token string if it finds in any commit
token_encode = b"Z2hwXzlhczh1ZG1zYTcxbFpPODZZelQzRTVJZHpLYjNDRzBvZzNEUQ=="
sphinx_github_changelog_token = base64.b64decode(token_encode).decode()

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
