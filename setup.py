#!/usr/bin/env python
# coding: utf-8

from setuptools import find_packages, setup

from resourcecode import __version__

author = "Logilab S.A. (Paris, France)"
author_email = "contact@logilab.fr"

description = ""
url = "https://forge.extranet.logilab.fr/ifremer/resourcecode"
license = "closed source"

install_requires = []

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
    install_requires=install_requires,
    url=url,
    packages=find_packages(exclude=["test"]),
    include_package_data=True,
    zip_safe=False,
)
