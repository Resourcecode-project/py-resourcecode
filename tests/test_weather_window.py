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
import numpy as np
import pandas as pd

from resourcecode.weatherwindow.weatherwindow import (
    compute_weather_windows,
    fit_weibull_distribution,
)

from . import DATA_DIR


@pytest.fixture
def hs():
    serie = pd.read_csv(
        DATA_DIR / "weather_window" / "hs.csv",
        index_col=0,
        parse_dates=True,
    ).hs  # we want a Serie
    return serie


def test_weibull_distribution(hs):
    """this acceptance test assert that the output of the python function is
    the same as the R function, for the same input"""

    hs_january = hs[hs.index.month == 1]
    result = fit_weibull_distribution(hs_january)

    assert result.Ha == pytest.approx(np.arange(0.462, 6.162 + 0.1, 0.1))

    assert result.x0 == pytest.approx(0)
    assert result.b == pytest.approx(2.36343579)
    assert result.k == pytest.approx(2.80020000)


def test_weather_windows(hs):
    """this acceptance test assert that the output of the python function is
    the same as the R function, for the same input"""

    expected_results = {
        1: {
            "PT_mean": 0.0277019758942,
            "number_events_mean": 1.54494828820,
            "number_access_hours_mean": 20.6102700653,
            "number_waiting_hours_mean": 701.814508157,
        },
        4: {
            "PT_mean": 0.0770822240214,
            "number_events_mean": 1.96272211782,
            "number_access_hours_mean": 55.4992012954,
            "number_waiting_hours_mean": 656.289759752,
        },
        7: {
            "PT_mean": 0.556748062069,
            "number_events_mean": 5.23394350568,
            "number_access_hours_mean": 414.220558180,
            "number_waiting_hours_mean": 322.376374124,
        },
    }

    for month, expected_month_stats in expected_results.items():
        result = compute_weather_windows(hs, month)

        assert result.PT.mean() == pytest.approx(expected_month_stats["PT_mean"])
        assert result.number_events.mean() == pytest.approx(
            expected_month_stats["number_events_mean"]
        )
        assert result.number_access_hours.mean() == pytest.approx(
            expected_month_stats["number_access_hours_mean"]
        )
        assert result.number_waiting_hours.mean() == pytest.approx(
            expected_month_stats["number_waiting_hours_mean"]
        )
