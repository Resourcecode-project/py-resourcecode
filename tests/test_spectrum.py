# coding: utf-8

# Copyright 2020-2022 IFREMER (Brest, FRANCE), all rights reserved.
# contact -- mailto:nicolas.raillard@ifremer.fr
#
# This file is part of Resourcecode.
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

import numpy as np
import xarray
import pytest

from resourcecode.spectrum import (
    raw_convert_spectrum_2Dto1D,
    raw_compute_parameters_from_1D_spectrum,
    raw_compute_parameters_from_2D_spectrum,
    get_2D_spectrum,
    get_1D_spectrum,
    plot_2D_spectrum,
    plot_1D_spectrum,
)

from resourcecode.spectrum.compute_parameters import SeaStatesParameters

from . import DATA_DIR


def test_convert_spectrum_2D_to_1D():
    spec = np.loadtxt(DATA_DIR / "spectrum" / "spec.csv", delimiter=",")
    vdir = np.loadtxt(DATA_DIR / "spectrum" / "dir.csv", delimiter=",")

    expected_1D_spectrum = np.loadtxt(DATA_DIR / "spectrum" / "Etfh.csv", delimiter=",")
    got_1D_spectrum = raw_convert_spectrum_2Dto1D(spec, vdir)

    assert got_1D_spectrum == pytest.approx(expected_1D_spectrum)


def test_compute_parameter_1D():
    freq = np.loadtxt(DATA_DIR / "spectrum" / "freq.csv", delimiter=",")
    depth = float(np.loadtxt(DATA_DIR / "spectrum" / "depth.csv", delimiter=","))
    etfh = np.loadtxt(DATA_DIR / "spectrum" / "Etfh.csv", delimiter=",")

    expected_parameters = SeaStatesParameters(
        *np.loadtxt(DATA_DIR / "spectrum" / "parameters_1D.csv", delimiter=",")
    )
    got_parameters = raw_compute_parameters_from_1D_spectrum(etfh, freq, depth)

    assert got_parameters.approx(expected_parameters)


def test_compute_parameter_2D():
    spec = np.loadtxt(DATA_DIR / "spectrum" / "spec.csv", delimiter=",")
    freq = np.loadtxt(DATA_DIR / "spectrum" / "freq.csv", delimiter=",")
    vdir = np.loadtxt(DATA_DIR / "spectrum" / "dir.csv", delimiter=",")
    depth = float(np.loadtxt(DATA_DIR / "spectrum" / "depth.csv", delimiter=","))

    expected_parameters = SeaStatesParameters(
        *np.loadtxt(DATA_DIR / "spectrum" / "parameters_2D.csv", delimiter=",")
    )
    got_parameters = raw_compute_parameters_from_2D_spectrum(spec, freq, vdir, depth)

    assert got_parameters.approx(expected_parameters)


def test_download_2D_file():
    # Use decode_cf=False to avoid xarray segfault with scale_factor/add_offset
    # This is a workaround for xarray >= 2024.x with numpy 2.x where applying
    # CF conventions (scale_factor, add_offset) causes a segfault in some cases.
    # See, probably related to https://github.com/pydata/xarray/issues/11205 / numpy / xarray and
    # python 3.14
    expected_spectrum = xarray.open_dataset(
        DATA_DIR / "spectrum" / "W001933N55743_201605.nc",
        decode_cf=False,
    )
    # Manually apply scale_factor and add_offset
    efth_encoded = expected_spectrum["efth"]
    scale_factor = expected_spectrum["efth"].encoding.get("scale_factor", 1.0)
    add_offset = expected_spectrum["efth"].encoding.get("add_offset", 0.0)
    efth_decoded = efth_encoded * scale_factor + add_offset
    expected_spectrum = expected_spectrum.assign(
        Ef=np.power(10.0, efth_decoded) - 1e-12
    )
    expected_spectrum = expected_spectrum.drop_vars("efth")

    got_spectrum = get_2D_spectrum("W001933N55743", ["2016"], ["05"])

    assert all(got_spectrum == expected_spectrum)


def test_download_1D_file():
    expected_spectrum = xarray.open_dataset(
        DATA_DIR / "spectrum" / "RSCD_WW3-RSCD-UG-W001933N55743_201605_freq.nc"
    )
    expected_spectrum = expected_spectrum.drop_dims("string40").squeeze()
    expected_spectrum = expected_spectrum.drop_vars(["station"])

    got_spectrum = get_1D_spectrum("W001933N55743", ["2016"], ["05"])

    assert all(got_spectrum == expected_spectrum)


def test_get_fields_2D():
    got_spectrum = get_2D_spectrum("W001933N55743", ["2016"], ["05"])

    assert list(got_spectrum.keys()) == [
        "longitude",
        "latitude",
        "frequency1",
        "frequency2",
        "dpt",
        "wnd",
        "wnddir",
        "cur",
        "curdir",
        "Ef",
    ]


def test_get_fields_1D():
    got_spectrum = get_1D_spectrum("W001933N55743", ["2016"], ["05"])

    assert list(got_spectrum.keys()) == [
        "longitude",
        "latitude",
        "frequency1",
        "frequency2",
        "ef",
        "th1m",
        "th2m",
        "sth1m",
        "sth2m",
        "dpt",
        "wnd",
        "wnddir",
        "cur",
        "curdir",
        "hs",
        "fp",
        "f02",
        "f0m1",
        "th1p",
        "sth1p",
        "dir",
        "spr",
    ]


def test_plot_2D_spectrum():
    got_spectrum = get_2D_spectrum("W001933N55743", ["2016"], ["05"])
    fig = plot_2D_spectrum(got_spectrum, 10)
    fig.savefig("tests/output/2Dspec.png", bbox_inches="tight")


def test_plot_1D_spectrum():
    got_spectrum = get_1D_spectrum("W001933N55743", ["2016"], ["05"])
    fig = plot_1D_spectrum(got_spectrum, 10)
    fig.savefig("tests/output/1Dspec.png", bbox_inches="tight")
