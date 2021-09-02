#!/usr/bin/env python3
# coding: utf-8

import json
from typing import TYPE_CHECKING, BinaryIO, Union
from pathlib import Path

import xarray
import pandas as pd

from resourcecode.data import DATA_DIR

if TYPE_CHECKING:
    try:
        from dask.delayed import Delayed
    except ImportError:
        Delayed = None

with open(DATA_DIR / "netcfd_description.json") as fobj:
    NETCFD_DESCRIPTION = json.load(fobj)


def to_netcfd(
    dataframe: pd.DataFrame, path: Union[str, Path] = None
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


def read_netcfd(filename_or_obj: Union[str, Path, BinaryIO]) -> pd.DataFrame:
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
    `read_netcfd` is a simple helper to load netcdf files. Please refer to
    :py:func:`xarray.open_dataset` for more parameters if needs be.
    """

    xr = xarray.open_dataset(filename_or_obj=filename_or_obj, mask_and_scale=True)
    return xr.to_dataframe()
