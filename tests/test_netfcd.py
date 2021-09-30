#!/usr/bin/env python3
# coding: utf-8

import pandas as pd
import xarray
import pytest

# (needed to load to_netcdf and read_netcdf functions)
import resourcecode  # noqa


@pytest.fixture
def dataframe():
    return pd.DataFrame(
        [
            [
                1.0,
            ],
            [
                2.0,
            ],
            [
                3.0,
            ],
        ],
        columns=["hs"],
        index=pd.date_range("2020/01/01", "2020/01/03", freq="1D"),
    )


def test_import_export_cycle(dataframe):
    exported_netcdf = dataframe.to_netcdf()
    assert pd.read_netcdf(exported_netcdf).equals(dataframe)


def test_encoding_is_exported(dataframe):
    xr = xarray.open_dataset(dataframe.to_netcdf(), mask_and_scale=True)
    assert xr.hs.attrs["units"] == "m"
    assert xr.hs.attrs["long_name"] == "significant height of wind and swell waves"
    assert xr.hs.encoding["scale_factor"] == 0.002
