#!/usr/bin/env python3
# coding: utf-8

import pandas as pd
from pandas.core.base import PandasObject

from resourcecode.client import Client
from resourcecode.__version__ import __version__
from resourcecode.io import to_netcdf, read_netcdf
from resourcecode.data import (
    get_coastline,
    get_grid_field,
    get_grid_spec,
    get_islands,
    get_triangles,
    get_variables,
    get_closest_point,
    get_closest_station,
)

PandasObject.to_netcdf = to_netcdf
pd.read_netcdf = read_netcdf


__all__ = [
    "__version__",
    "Client",
    "get_coastline",
    "get_grid_field",
    "get_grid_spec",
    "get_islands",
    "get_triangles",
    "get_variables",
    "get_closest_station",
    "get_closest_point",
]
