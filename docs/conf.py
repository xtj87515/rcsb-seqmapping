# SPDX-FileCopyrightText: Copyright 2020-2023, Contributors to CICD
# SPDX-PackageHomePage: https://github.com/dmyersturnbull/cicd
# SPDX-License-Identifier: Apache-2.0

"""
Sphinx config file.

Uses several extensions to get API docs and sourcecode.
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

import tomllib as toml
from pathlib import Path
from typing import TypeVar

# This assumes that we have the full project root above, containing pyproject.toml
_root = Path(__file__).parent.parent.resolve()
_toml = toml.loads((_root / "pyproject.toml").read_text(encoding="utf8"))

T = TypeVar("T")


# Basic information, used by Sphinx
language = "en-US"
# :tyranno: project = "${project.name}"
project = "cicd"
# :tyranno: version = "${project.version}"
version = "0.0.0-alpha0"
release = version
author = "Contributors"

# Copyright string (for documentation)
# It's not clear whether we're supposed to, but we'll add the license
# noinspection PyShadowingBuiltins
# :tyranno: project = "${.copyright}"
copyright = "Copyright $2020-2023, Contributors to cicd"

source_suffix = [".rst", ".md"]


# Load extensions
# These should be in docs/requirements.txt
# Napoleon is bundled in Sphinx, so we don't need to list it there
# NOTE: 'autoapi' here refers to sphinx-autoapi
# See https://sphinx-autoapi.readthedocs.io/
extensions = [
    "sphinx.ext.napoleon",
    "sphinx_copybutton",
    "myst_parser",
    "autodoc2",
]
# myst_gfm_only = True
master_doc = "index"
napoleon_include_special_with_doc = True
autodoc2_packages = [str(_root / project)]
autodoc2_render_plugin = "myst"
# The vast majority of Sphinx themes are unmaintained
# This includes alabaster and readthedocs
# Furo is well-maintained as of 2023
# These can be specific to the theme, or processed by Sphinx directly
# https://www.sphinx-doc.org/en/master/usage/configuration.html
html_theme = "furo"

# doc types to build
sphinx_enable_epub_build = False
sphinx_enable_pdf_build = False
exclude_patterns = ["_build", "Thumbs.db", ".*", "~*", "*~", "*#"]
