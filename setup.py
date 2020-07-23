#!/usr/bin/env python
# coding: utf-8

from setuptools import find_packages, setup

author = "Logilab S.A. (Paris, France)"
author_email = "contact@logilab.fr"

numversion = (0, 1, 0)
version = ".".join(str(num) for num in numversion)

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
    version=version,
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
