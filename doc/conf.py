# coding: utf-8

# copyright 2021 IFREMER (Brest, FRANCE), all rights reserved.
# contact -- mailto:nicolas.raillard@ifremer.fr
#
# This file is part of Resourcecode.
#
# Resourcecode is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3.0 of the License, or (at your option)
# any later version.
#
# Resourcecode is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with Resourcecode. If not, see <https://www.gnu.org/licenses/>.

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
import sys
from pathlib import Path
from datetime import date

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))


# -- Project information -----------------------------------------------------

project = "Resourcecode"
copyright = f"{date.today():%Y}, IFREMER"
author = "IFREMER"

# The full version, including alpha/beta/rc tags
version_file = ROOT / "resourcecode" / "__version__.py"
__versioninfo__ = {}
with open(version_file) as f:
    exec(f.read(), __versioninfo__)

release = __versioninfo__["__version__"]


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
    "sphinx.ext.doctest",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_book_theme"
html_logo = "_static/resourcecode-logo.jpg"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
