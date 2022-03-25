# coding: utf-8

# copyright 2021 IFREMER (Brest, FRANCE), all rights reserved.
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
import pytest

from resourcecode.spectrum import (
    convert_spectrum_2Dto1D,
    compute_parameters_from_1D_spectrum,
    compute_parameters_from_2D_spectrum,
)

from resourcecode.spectrum.compute_parameters import SeaStatesParameters

from . import DATA_DIR


def test_convert_spectrum_2D_to_1D():
    spec = np.loadtxt(DATA_DIR / "spectrum" / "spec.csv", delimiter=",")
    vdir = np.loadtxt(DATA_DIR / "spectrum" / "dir.csv", delimiter=",")

    expected_1D_spectrum = np.loadtxt(DATA_DIR / "spectrum" / "Etfh.csv", delimiter=",")
    got_1D_spectrum = convert_spectrum_2Dto1D(spec, vdir)

    assert got_1D_spectrum == pytest.approx(expected_1D_spectrum)


def test_compute_parameter_1D():
    freq = np.loadtxt(DATA_DIR / "spectrum" / "freq.csv", delimiter=",")
    depth = float(np.loadtxt(DATA_DIR / "spectrum" / "depth.csv", delimiter=","))
    etfh = np.loadtxt(DATA_DIR / "spectrum" / "Etfh.csv", delimiter=",")

    expected_parameters = SeaStatesParameters(
        *np.loadtxt(DATA_DIR / "spectrum" / "parameters_1D.csv", delimiter=",")
    )
    got_parameters = compute_parameters_from_1D_spectrum(etfh, freq, depth)

    assert got_parameters == pytest.approx(expected_parameters)


def test_compute_parameter_2D():
    spec = np.loadtxt(DATA_DIR / "spectrum" / "spec.csv", delimiter=",")
    freq = np.loadtxt(DATA_DIR / "spectrum" / "freq.csv", delimiter=",")
    vdir = np.loadtxt(DATA_DIR / "spectrum" / "dir.csv", delimiter=",")
    depth = float(np.loadtxt(DATA_DIR / "spectrum" / "depth.csv", delimiter=","))

    expected_parameters = SeaStatesParameters(
        *np.loadtxt(DATA_DIR / "spectrum" / "parameters_2D.csv", delimiter=",")
    )
    got_parameters = compute_parameters_from_2D_spectrum(spec, freq, vdir, depth)

    assert got_parameters == pytest.approx(expected_parameters)
