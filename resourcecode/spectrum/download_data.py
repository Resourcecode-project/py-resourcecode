# coding: utf-8

# Copyright 2020-2022  IFREMER (Brest, FRANCE), all rights reserved.
# contact -- mailto:nicolas.raillard@ifremer.fr
#
# This file is part of Resourcecode.
# Based on a matlab code written by Christophe Maisondieu (christophe.maisondieu@ifremer.fr)
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

import shutil
import tempfile
import urllib.request
import xarray
from typing import Iterable

from resourcecode.data import get_grid_spec, get_covered_period


def download_single_file(
    point: str,
    year: str,
    month: str,
) -> xarray.Dataset:
    """
    Download the 2D spectrum data from IFREMER ftp

    Parameters
    ----------

    point:
        the location name (string) requested. The consistency is checked internally.
    year:
        the year (as a string) requested. The consistency is checked internally.
    month:
        the month number, as a string, with a leading zero

    Return
    ------

    res:
        A dataset object with the data read from the downloaded netCDF file.
    """
    base = "ftp://ftp.ifremer.fr/ifremer/dataref/ww3/resourcecode/HINDCAST/"
    url = (
        base
        + year
        + "/"
        + month
        + "/SPEC_NC/RSCD_WW3-RSCD-UG-"
        + point
        + "_"
        + year
        + month
        + "_spec.nc"
    )

    if point not in set(get_grid_spec().name):
        raise ValueError(f"{point} is an unkown location")

    if (
        int(year)
        < get_covered_period()["start"].year | int(year)
        >= get_covered_period()["end"].year
    ):
        raise ValueError(f"{year} is outsite the covered period")

    if int(month) < 1 | int(month) > 12:
        raise ValueError(f"{month} must by between 1 and 12 with a leading zero")

    with urllib.request.urlopen(url) as response:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".nc") as tmp_file:
            shutil.copyfileobj(response, tmp_file)
    X = xarray.open_dataset(tmp_file.name).drop_dims("string40").squeeze()
    return X


def download_spec(
    point: str,
    years: Iterable[str],
    months: Iterable[str],
) -> xarray.Dataset:
    """
    Download the 2D spectrum data from IFREMER ftp

    Parameters
    ----------

    point:
        the location name (string) requested. The consistency is checked internally.
    years:
        the years (list of string) requested. The consistency is checked internally.
    months:
        the month number (list of string), with a trailing zero.

    Return
    ------

    res:
        A dataset object with the data read from the downloaded netCDF file.
    """
    datasets = []
    for yr in years:
        for mth in months:
            ds = download_single_file(point, yr, mth)
            datasets.append(ds)
    result = xarray.concat(datasets, dim="time")
    return result
