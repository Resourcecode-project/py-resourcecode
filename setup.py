#!/usr/bin/env python
# coding: utf-8

from pathlib import Path
from setuptools import find_packages, setup

HERE = Path(__file__).parent

version_context = {}
with open(HERE / "resourcecode" / "__version__.py") as f:
    exec(f.read(), version_context)

author = "Logilab S.A. (Paris, France)"
author_email = "contact@logilab.fr"

description = ""
url = "https://forge.extranet.logilab.fr/ifremer/resourcecode"
license = "closed source"

install_requires = [
    "requests >= 2.23.0",
]

classifiers = [
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
]

setup(
    name="resourcecode",
    version=version_context["__version__"],
    license=license,
    description=description,
    author=author,
    author_email=author_email,
    install_requires=install_requires,
    url=url,
    packages=find_packages(exclude=["test"]),
    data_files=[("etc/resourcecode", ["config/config.ini"])],
    include_package_data=True,
    zip_safe=False,
)
