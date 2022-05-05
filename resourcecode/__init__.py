# coding: utf-8

# Copyright 2020-2022 IFREMER (Brest, FRANCE), all rights reserved.
# contact -- mailto:nicolas.raillard@ifremer.fr
#
# This file is part of Resourcecode.
# Written by Logilab SA (contact@logilab.fr)
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

import pandas as pd
from pandas.core.base import PandasObject
import plotly.io as pio

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

# load the resourcecode plotly theme
import resourcecode.plotly_theme  # noqa

pio.templates.default = "plotly+resourcecode"

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
