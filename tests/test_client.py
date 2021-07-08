#!/usr/bin/env python3
# coding: utf-8

import json
from unittest import mock

import pytest
import pandas as pd

import resourcecode

from . import DATA_DIR


def mock_requests_get_raw_data(query_url, parameters):
    """this function mocks the 'requests.get' call in the `_get_rawdata` method
    of the Client.

    it reads the parameters given `requests.get` call, opens the corresponding
    file, and return a Response object. This Response object is a Mock, which
    has one attribute `ok` (True if a file has been read, False otherwise), and
    one method `json`. Calling this method will return the content of the
    requested file.
    """

    mocked_response = mock.Mock()
    parameter = parameters.get("parameter", [None])[0]
    data_path = DATA_DIR / f"timeseries_{parameter}.json"

    if not data_path.exists():
        mocked_response.ok = False
        return mocked_response

    with open(data_path) as fobj:
        mocked_response.json.return_value = json.load(fobj)

    mocked_response.ok = True
    return mocked_response


@pytest.fixture
def client():
    """This fixture returns a « fake client » in the sense that the requests.get
    function is mocked to return a file from the DATA_DIR directory.

    Except for that, this client is exactly as the "real" client.

    """
    client = resourcecode.Client()
    with mock.patch("requests.get", side_effect=mock_requests_get_raw_data):
        yield client


def test_import_client():
    """a dummy test that instantiate a client."""
    # remove this tests when a real test can be achieved.
    client = resourcecode.Client()
    assert client.config.get("default", "cassandra-base-url")


def test_get_raw_data():
    parameter = "fp"
    client = resourcecode.Client()

    with mock.patch(
        "requests.get", side_effect=mock_requests_get_raw_data
    ) as mock_requests_get:
        json_data = client._get_rawdata_from_criteria(
            {
                "parameter": [
                    parameter,
                ]
            }
        )

    mock_requests_get.assert_called_once_with(
        client.cassandra_base_url + "api/timeseries", {"parameter": [parameter]}
    )
    assert json_data["query"]["parameterCode"] == parameter

    dataset_size = json_data["result"]["dataSetSize"]
    assert len(json_data["result"]["data"]) == dataset_size


def test_get_criteria_single_parameter(client):
    data = client.get_dataframe_from_criteria('{"parameter": ["fp"]}')

    assert len(data) == 744
    assert (data.columns == ["fp"]).all()
    assert data.index[0] == pd.to_datetime("2017-01-01 00:00:00")
    assert data.index[-1] == pd.to_datetime("2017-01-31 23:00:00")
    assert data.fp[0] == pytest.approx(0.074)
    assert data.fp[-1] == pytest.approx(0.097)


def test_get_criteria_single_tp_parameter(client):
    data = client.get_dataframe_from_criteria('{"parameter": ["tp"]}')

    assert len(data) == 744
    assert (data.columns == ["tp"]).all()
    assert data.index[0] == pd.to_datetime("2017-01-01 00:00:00")
    assert data.index[-1] == pd.to_datetime("2017-01-31 23:00:00")
    assert data.tp[0] == pytest.approx(13.51351)
    assert data.tp[-1] == pytest.approx(10.30928)


def test_get_criteria_multiple_parameters(client):
    data = client.get_dataframe_from_criteria('{"parameter": ["fp", "hs"]}')

    assert len(data) == 744
    assert (data.columns == ["fp", "hs"]).all()
    assert data.index[0] == pd.to_datetime("2017-01-01 00:00:00")
    assert data.index[-1] == pd.to_datetime("2017-01-31 23:00:00")
    assert data.fp[0] == pytest.approx(0.074)
    assert data.fp[-1] == pytest.approx(0.097)
    assert data.hs[0] == pytest.approx(0.296)
    assert data.hs[-1] == pytest.approx(0.756)


def test_get_criteria_multiple_parameters_and_none_values(client):
    data = client.get_dataframe_from_criteria('{"parameter": ["uust"]}')

    assert len(data) == 744
    assert (data.columns == ["uust"]).all()

    # the first value of uust in null, and there is no other variable, therefore
    # the first index remains unknown
    assert pd.isnull(data.index[0])
    assert pd.isnull(data.uust[0])

    # the third value is not null.
    assert data.index[2] == pd.to_datetime("2017-01-01 02:00:00")
    assert data.uust[2] == pytest.approx(0.1699999962)

    data = client.get_dataframe_from_criteria('{"parameter": ["uust", "fp"]}')

    assert len(data) == 744
    assert (data.columns == ["uust", "fp"]).all()

    # in that case, we have two variables. The second one, fp, is not null,
    # therefore the index can be completed despite that uust is null.
    assert data.index[0] == pd.to_datetime("2017-01-01 00:00:00")
    assert data.index[-1] == pd.to_datetime("2017-01-31 23:00:00")

    assert data.fp[0] == pytest.approx(0.074)
    assert data.fp[-1] == pytest.approx(0.097)
    assert pd.isnull(data.uust[0])
    assert data.uust[2] == pytest.approx(0.1699999962)
