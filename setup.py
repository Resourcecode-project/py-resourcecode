# coding: utf-8

# copyright 2021 IFREMER (Brest, FRANCE), all rights reserved.
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
url = "https://gitlab.ifremer.fr/resourcecode/resourcecode"
license = "GPL-v3.0"

install_requires = [
    "pandas >= 1.0.0",
    "requests >= 2.23.0",
    "numpy >= 1.20.1, < 2.0.0",
    "scipy >= 1.6.1, < 2.0.0",
    "pyextremes >= 2.0.0, < 3.0.0",
    "pyarrow >= 4.0.0, < 5.0.0",
    "plotly >= 4.12.0, < 5.0.0",
    "numexpr >= 2.7.0, < 3.0.0",
    "xarray >= 0.19.0, < 1.0.0",
]

classifiers = [
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
]

setup(
    name="resourcecode",
    version=__version__,
    license=license,
    description=description,
    author=author,
    author_email=author_email,
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    install_requires=install_requires,
    url=url,
    packages=find_packages(exclude=["test"]),
    data_files=[("etc/resourcecode", ["config/config.ini"])],
    include_package_data=True,
    zip_safe=False,
)
