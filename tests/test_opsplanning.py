#!/usr/bin/env python3
# coding: utf-8

import pytest
import pandas as pd
import numpy as np

from resourcecode.opsplanning import ww_calc, wwmonstats

from . import DATA_DIR


@pytest.fixture
def data():
    df = pd.read_csv(
        DATA_DIR / "opsplanning" / "input.csv",
        index_col=0,
        parse_dates=True,
        dayfirst=True,
    )
    return df


@pytest.fixture
def criteria():
    return "hs < 2 and tp < 3"


def test_ww_calc_concurrent_window(data, criteria):
    critsubs = data.query(criteria)
    got_windows = ww_calc(critsubs, winlen=1, concurrent_windows=True)

    assert (
        got_windows.values
        == np.array(
            [
                "2005-02-27T21:00:00.000000000",
                "2005-02-27T23:00:00.000000000",
                "2005-02-28T01:00:00.000000000",
                "2005-03-03T13:00:00.000000000",
                "2005-05-11T01:00:00.000000000",
                "2005-06-18T05:00:00.000000000",
                "2005-06-18T07:00:00.000000000",
                "2005-06-22T22:00:00.000000000",
                "2005-06-26T14:00:00.000000000",
                "2005-07-17T04:00:00.000000000",
                "2005-07-17T06:00:00.000000000",
                "2005-07-17T18:00:00.000000000",
                "2005-08-02T06:00:00.000000000",
                "2005-08-15T06:00:00.000000000",
                "2005-10-13T20:00:00.000000000",
                "2005-11-19T23:00:00.000000000",
            ],
            dtype=np.datetime64,
        )
    ).all()


def test_ww_calc_continuous_window(data, criteria):
    critsubs = data.query(criteria)
    got_windows = ww_calc(critsubs, winlen=1, concurrent_windows=False)

    assert (
        got_windows.values
        == np.array(
            [
                "2005-02-27T21:00:00.000000000",
                "2005-02-27T22:00:00.000000000",
                "2005-02-27T23:00:00.000000000",
                "2005-02-28T00:00:00.000000000",
                "2005-02-28T01:00:00.000000000",
                "2005-03-03T13:00:00.000000000",
                "2005-03-03T14:00:00.000000000",
                "2005-05-11T01:00:00.000000000",
                "2005-06-18T05:00:00.000000000",
                "2005-06-18T06:00:00.000000000",
                "2005-06-18T07:00:00.000000000",
                "2005-06-22T22:00:00.000000000",
                "2005-06-26T14:00:00.000000000",
                "2005-07-17T04:00:00.000000000",
                "2005-07-17T05:00:00.000000000",
                "2005-07-17T06:00:00.000000000",
                "2005-07-17T18:00:00.000000000",
                "2005-08-02T06:00:00.000000000",
                "2005-08-02T07:00:00.000000000",
                "2005-08-15T06:00:00.000000000",
                "2005-10-13T20:00:00.000000000",
                "2005-11-19T23:00:00.000000000",
                "2005-11-20T00:00:00.000000000",
            ],
            dtype=np.datetime64,
        )
    ).all()


def test_wwmonstats(data, criteria):
    critsubs = data.query(criteria)
    windows = ww_calc(critsubs, winlen=1)
    got_stats = wwmonstats(windows)

    expected_stats = pd.DataFrame(
        [
            [
                3.0,
                1.0,
                1.0,
                4.0,
                3.0,
                2.0,
                1.0,
                1.0,
            ]
        ],
        columns=[2, 3, 5, 6, 7, 8, 10, 11],
        index=[2005],
    )

    assert expected_stats.equals(got_stats)
