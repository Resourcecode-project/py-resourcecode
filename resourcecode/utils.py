#!/usr/bin/env python3
# coding: utf-8

import os
import sys
import configparser
import logging
from pathlib import Path

from numpy import triu_indices, tril_indices

CONFIG_FILEPATHS = [
    os.environ.get("RESOURCECODE_CONFIG_FILEPATH"),
    "./resourcecode.ini",
    "~/.config/resourcecode.ini",
    f"{sys.prefix}/etc/resourcecode/config.ini",
]

LOGGER = logging.getLogger("resourcecode.default")
LOGGER.addHandler(logging.StreamHandler())
LOGGER.setLevel(os.environ.get("RESOURCECODE_LOG_THRESHOLD", "WARNING"))


def get_config():
    config = configparser.ConfigParser()
    for config_filepath in CONFIG_FILEPATHS:
        LOGGER.debug("try reading config from %s", config_filepath)
        if not config_filepath:
            continue

        config_filepath = Path(config_filepath).expanduser()
        if not config_filepath.exists():
            continue

        config.read(config_filepath)
        LOGGER.info("config loaded from %s", config_filepath)
        break
    else:
        raise FileNotFoundError("no config file was found")
    return config


def set_trig(m, values, part="upper"):
    """Set the `values` upper/lower `part` of the square matrix `m`"""
    part = part.lower()
    if part == "upper":
        tri_indices = triu_indices(len(values), k=1)
    elif part == "lower":
        tri_indices = tril_indices(len(values), k=-1)
    else:
        raise ValueError(f"part must be 'lower' or 'upper', '{part}' given")

    for n, (i, j) in enumerate(zip(*tri_indices)):
        m[i, j] = values[n]
