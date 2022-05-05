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

from resourcecode.resassess import exceed, bivar_stats, univar_monstats

from . import DATA_DIR


@pytest.fixture
def data():
    df = pd.read_csv(
        DATA_DIR / "resassess" / "input.csv",
        index_col=0,
        parse_dates=True,
    )
    return df


def test_exceed():
    data = pd.Series(np.arange(1, 5))
    sorted_data, exceedance = exceed(data)
    np.testing.assert_array_equal(sorted_data.values, np.arange(4, 0, -1))
    np.testing.assert_array_equal(exceedance, [0.75, 0.5, 0.25, 0.0])


def test_bivar_stats_missing_column():
    data = pd.DataFrame()
    with pytest.raises(NameError) as e:
        bivar_stats(data)
    assert e.match("Crucial parameter missing: cge, hs, t0m1")

    data = pd.DataFrame({"hs": [], "cge": [], "loutre": []})
    with pytest.raises(NameError) as e:
        bivar_stats(data)
    assert e.match("Crucial parameter missing: t0m1")


def test_univar_monstats_missing_columns():
    data = pd.DataFrame({"toto": []})
    with pytest.raises(NameError) as e:
        univar_monstats(data, "hs")
    error_msg = "Parameter hs is not in the dataframe. Possible values are: toto"
    assert e.match(error_msg)


def test_bivar_stats(data):
    all_df_results = bivar_stats(data)
    stored_results = (
        ("percentage", "df_percentage_occurence.csv"),
        ("count", "df_number_occurence.csv"),
        ("mean", "df_average_energy.csv"),
        ("stdev", "df_standard_deviation_energy.csv"),
    )
    statistics = [stat for stat, _ in stored_results]
    existing_statistics = all_df_results.columns.levels[0].to_list()
    assert sorted(existing_statistics) == sorted(statistics)
    for stat, expected_result_path in stored_results:
        path = DATA_DIR / "resassess" / expected_result_path
        expected_result = pd.read_csv(path, index_col=0)
        np.testing.assert_allclose(all_df_results[stat], expected_result, rtol=1e-13)


def test_univar_monstats(data):
    exceed, dtm, dty = univar_monstats(data, "hs")
    stored_results = ("monthly_stat.csv", "yearly_stat.csv")
    for result, expected_result_path in zip((dtm, dty), stored_results):
        path = DATA_DIR / "resassess" / expected_result_path
        expected_result = pd.read_csv(path, index_col=0)
        # count is the first column return by describe
        count_index = result.columns.get_loc("count")

        # Check the first columns that could either be int (month_index, year) or
        # string (month)
        assert result.iloc[:, :count_index].equals(
            expected_result.iloc[:, :count_index]
        )
        # Check the remaining columns (floats) using numpy
        np.testing.assert_allclose(
            result.iloc[:, count_index:],
            expected_result.iloc[:, count_index:],
            rtol=1e-15,
        )
