#!/usr/bin/env python3
# coding: utf-8

from resourcecode.utils import get_config


class Client:
    def __init__(self):
        self.config = get_config()
