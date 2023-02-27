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

import json
from typing import Optional, TYPE_CHECKING, Union, Any
from os import PathLike
from io import BufferedIOBase
from pathlib import Path

import xarray
from xarray.backends.common import AbstractDataStore
import pandas as pd

from resourcecode.data import DATA_DIR

if TYPE_CHECKING:
    try:
        from dask.delayed import Delayed
    except ImportError:
        Delayed = None

with open(DATA_DIR / "netcdf_description.json") as fobj:
    NETCFD_DESCRIPTION = json.load(fobj)


def to_netcdf(
    dataframe: pd.DataFrame, path: Optional[Union[str, Path]] = None
) -> Union[bytes, "Delayed", None]:
    """Write dataframe contents to a netCFD file.

    Parameters
    ----------
    path: str, Path or file-like, optional
        Path to which to save this dataset. File-like objects are only supported
        by the scipy engine. If no path is provided, this function returns the
        resulting netCDF file as bytes; in this case, we need to use scipy,
        which does not support netCDF version 4 (the default format becomes
        NETCDF3_64BIT).

    """
    xr = dataframe.to_xarray()
    for variable in xr:
        variable_attrs = NETCFD_DESCRIPTION.get(variable, {})
        if not variable_attrs:
            continue

        scale_factor = variable_attrs.get("scale_factor", 1)
        add_offset = variable_attrs.get("add_offset", 0)

        xr[variable] = (xr[variable] - add_offset) / scale_factor
        xr[variable].attrs.update(variable_attrs)
    return xr.to_netcdf(path)


def read_netcdf(
    filename_or_obj: Union[str, PathLike[Any], BufferedIOBase, AbstractDataStore]
) -> pd.DataFrame:
    """Open and decode a dataframe from a file or file-like object.

    Parameters
    ----------
    filename_or_obj: str, Path, file-like
        Strings and Path objects are interpreted as a path to a netCDF file
        or an OpenDAP URL and opened with python-netCDF4, unless the filename
        ends with .gz, in which case the file is gunzipped and opened with
        scipy.io.netcdf (only netCDF3 supported). Byte-strings or file-like
        objects are opened by scipy.io.netcdf (netCDF3) or h5py (netCDF4/HDF).

    Returns
    -------
    dataframe: pd.DataFrame
        The newly created dataset.

    Notes
    -----
    `read_netcdf` is a simple helper to load netcdf files. Please refer to
    :py:func:`xarray.open_dataset` for more parameters if needs be.
    """

    xr = xarray.open_dataset(filename_or_obj=filename_or_obj, mask_and_scale=True)
    return xr.to_dataframe()
