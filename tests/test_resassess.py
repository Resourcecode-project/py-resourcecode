#!/usr/bin/env python3
# coding: utf-8

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


def test_bivar_stats(data):
    all_df_results = bivar_stats(data)
    stored_results = (
        "df_percentage_occurence.csv",
        "df_nubmer_occurence.csv",
        "df_average_energy.csv",
        "df_standard_deviation_energy.csv",
    )
    for result, expected_result_path in zip(all_df_results, stored_results):
        path = DATA_DIR / "resassess" / expected_result_path
        expected_result = pd.read_csv(path, index_col=0)
        np.testing.assert_allclose(result, expected_result, rtol=1e-13)


def test_univar_monstats(data):
    dtm, dty = univar_monstats(data, "hs", display=False)
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
