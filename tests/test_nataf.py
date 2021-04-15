#!/usr/bin/env python3
# coding: utf-8

import pytest
import numpy as np
import pandas as pd

from resourcecode.cengaussfit import cengaussfit

from . import DATA_DIR


def test_cengaussfit_acceptance():
    """this acceptance test assert that the output of the python function is
    the same as the R function, for the same input"""

    quant = 0.9
    X = np.loadtxt(
        DATA_DIR / "cengaussfit" / "input_0.csv",
        usecols=(1, 2, 3),
        delimiter=",",
        skiprows=1,
    )

    data = cengaussfit(X, quant)
    expected = np.loadtxt(
        DATA_DIR / "cengaussfit" / "output_0.csv",
        usecols=(1,),
        delimiter=",",
        skiprows=1,
    )
    assert data.success is True
    assert data.x == pytest.approx(expected, rel=1e-3)


