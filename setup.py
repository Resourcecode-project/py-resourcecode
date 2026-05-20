# coding: utf-8

# Copyright 2020-2023 IFREMER (Brest, FRANCE), all rights reserved.
# contact -- mailto:nicolas.raillard@ifremer.fr
#
# This file is part of Resourcecode.
#
# Resourcecode is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3.0 of the License, or any later version.
#
# Resourcecode is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along
# with Resourcecode. If not, see <https://www.gnu.org/licenses/>.

from pathlib import Path
from setuptools import find_packages, setup

HERE = Path(__file__).parent

version_context = {}
with open(HERE / "resourcecode" / "__version__.py") as f:
    exec(f.read(), version_context)

author = "Nicolas Raillard (IFREMER, Brest)"
author_email = "nicolas.raillard@ifremer.fr"
__version__ = version_context["__version__"]

description = "The ResourceCODE Marine Data Toolbox is a python package to facilitate the\
 access to recent hindcast database of sea-state , along with a set of state-of-the-art methods for data analysis."
url = "https://resourcecode-project.github.io/py-resourcecode/"
license = "GPL-v3.0"

install_requires = [
    "pandas >= 1.5.3, < 3.0.0",
    "requests >= 2.28.1",
    "numpy >= 1.24.2, < 3.0.0",
    "scipy >= 1.10.1",
    "pyextremes >= 2.5.0",
    "pytest >= 7.2.1",
    "pyarrow >= 23.0.1",
    "plotly >= 5.4.0",
    "numexpr >= 2.8.4",
    "xarray >= 2026.4.0",
    "netCDF4 >= 1.7.4",
]

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Science/Research",
    "Intended Audience :: Developers",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3 :: Only",
    "Operating System :: OS Independent",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Topic :: Scientific/Engineering",
    "Topic :: Scientific/Engineering :: Mathematics",
    "Topic :: Scientific/Engineering :: Physics",
]

keywords = [
    "statistics",
    "extreme",
    "extreme value analysis",
    "eva",
    "coastal",
    "ocean",
    "marine",
    "environmental",
    "engineering",
    "renewable",
    "MRE",
    "offshore",
    "data",
    "hindcast",
]

setup(
    name="resourcecode",
    version=__version__,
    license=license,
    python_requires=">=3.9, <3.15",
    description=description,
    author=author,
    author_email=author_email,
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    install_requires=install_requires,
    classifiers=classifiers,
    keywords=keywords,
    url=url,
    packages=find_packages(exclude=["test"]),
    include_package_data=True,
    zip_safe=False,
    project_urls={
        "GitHub": "https://github.com/Resourcecode-project/py-resourcecode",
        "Web Portal": "https://resourcecode.ifremer.fr",
        "PyPI": "https://pypi.org/project/resourcecode",
    },
)
