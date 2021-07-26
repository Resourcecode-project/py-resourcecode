#!/usr/bin/env python3
# coding: utf-8

import numpy as np
import pytest

from resourcecode.spectrum import convert_spectrum_2Dto1D

from . import DATA_DIR


def test_convert_spectrum_2D_to_1D():
    spec = np.loadtxt(DATA_DIR / "spectrum" / "spec.csv", delimiter=",")
    vdir = np.loadtxt(DATA_DIR / "spectrum" / "dir.csv", delimiter=",")

    expected_1D_spectrum = np.loadtxt(DATA_DIR / "spectrum" / "Etfh.csv", delimiter=",")
    got_1D_spectrum = convert_spectrum_2Dto1D(spec, vdir)

    assert got_1D_spectrum == pytest.approx(expected_1D_spectrum)
