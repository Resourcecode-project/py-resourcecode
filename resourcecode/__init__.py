#!/usr/bin/env python3
# coding: utf-8

from resourcecode.client import Client

numversion = (0, 1, 0)
__version__ = ".".join(str(num) for num in numversion)

__all__ = [
    "Client",
]
