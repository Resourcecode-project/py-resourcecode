#!/usr/bin/env python3
# coding: utf-8

import os
import sys
import configparser
import logging
from pathlib import Path

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
