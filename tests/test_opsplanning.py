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

import pytest
import pandas as pd
import numpy as np

from resourcecode.opsplanning import ww_calc, wwmonstats, oplen_calc, olmonstats

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


def test_oplen_calc_non_critical_operation(data, criteria):
    critsubs = data.query(criteria)

    oplendetect_got = oplen_calc(critsubs, oplen=10, critical_operation=False)

    expected_operational_length_hours = pd.to_timedelta(
        [
            "91 days 15:00:00",
            "98 days 23:00:00",
            "69 days 12:00:00",
            "39 days 12:00:00",
            "17 days 08:00:00",
            "32 days 08:00:00",
            "62 days 10:00:00",
            "82 days 00:00:00",
            "68 days 13:00:00",
            " 0 days 00:00:00",
            " 0 days 00:00:00",
        ]
    )

    assert (oplendetect_got.values == expected_operational_length_hours.values).all()


def test_oplen_calc_critical_operation(data, criteria):
    critsubs = data.query(criteria)

    oplendetect_got = oplen_calc(critsubs, oplen=3, critical_operation=True)
    expected_operational_length_hours = pd.to_timedelta(
        [
            " 26 days 23:00:00",
            "109 days 08:00:00",
            " 78 days 08:00:00",
            " 48 days 08:00:00",
            " 17 days 08:00:00",
            " 16 days 07:00:00",
            "  0 days 00:00:00",
            "  0 days 00:00:00",
            "  0 days 00:00:00",
            " 19 days 01:00:00",
            "  0 days 00:00:00",
        ]
    )

    assert (oplendetect_got.values == expected_operational_length_hours.values).all()


def test_olmonstats(data, criteria):
    critsubs = data.query(criteria)
    oplendetect = oplen_calc(critsubs, oplen=10)
    got_stats = olmonstats(oplendetect)

    expected_stats = pd.DataFrame(
        [
            [
                2199.0,
                2375.0,
                1668.0,
                948.0,
                416.0,
                776.0,
                1498.0,
                1968.0,
                1645.0,
                0.0,
                0.0,
            ]
        ],
        columns=range(2, 13),
        index=[2005],
    )

    assert expected_stats.equals(got_stats)
