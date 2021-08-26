#!/usr/bin/env python3
# coding: utf-8

import pytest
import pandas as pd
import numpy as np

from resourcecode.resassess import exceed

from . import DATA_DIR


@pytest.fixture
def data():
    df = pd.read_csv(
        DATA_DIR / "resassess" / "input.csv",
        index_col=0,
        parse_dates=True,
    )
    return df


def test_exceed(data):
    data = pd.Series(np.arange(1, 5))
    sorted_data, exceedance = exceed(data)
    np.testing.assert_array_equal(sorted_data.values, np.arange(4, 0, -1))
    np.testing.assert_array_equal(exceedance, [0.75, 0.5, 0.25, 0.0])
