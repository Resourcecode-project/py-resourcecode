#!/usr/bin/env python3
# coding: utf-8


class BadParameterError(ValueError):
    """Exception raised when user queried an unknown parameter"""

    pass


class BadPointIdError(ValueError):
    """Exception raised when user queried an unknown pointId"""

    pass
