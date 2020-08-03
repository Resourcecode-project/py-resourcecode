#!/usr/bin/env python3
# coding: utf-8

import json
from pathlib import Path
from unittest import mock


import resourcecode

DATA_DIR = Path(__file__).parent / "data"


def mock_requests_get_raw_data(query_url, parameters):
    """ this function mocks the 'requests.get' call in the `_get_rawdata` method
    of the Client.

    it reads the parameters given `requests.get` call, opens the corresponding
    file, and return a Response object. This Response object is a Mock, which
    has one attribute `ok` (True if a file has been read, False otherwise), and
    one method `json`. Calling this method will return the content of the
    requested file.
    """

    mocked_response = mock.Mock()
    if "fp" in parameters["parameter"]:
        data_path = DATA_DIR / "timeseries_fp.json"
    elif "hs" in parameters["parameter"]:
        data_path = DATA_DIR / "timeseries_hs.json"
    else:
        mocked_response.ok = False
        return mocked_response

    with open(data_path) as fobj:
        mocked_response.json.return_value = json.load(fobj)

    mocked_response.ok = True
    return mocked_response


def test_import_client():
    """ a dummy test that instantiate a client.
    """
    # remove this tests when a real test can be achieved.
    client = resourcecode.Client()
    assert client.config.get("default", "cassandra-base-url")


def test_get_raw_data():
    parameter = "fp"
    client = resourcecode.Client()

    with mock.patch(
        "requests.get", side_effect=mock_requests_get_raw_data
    ) as mock_requests_get:
        json_data = client._get_rawdata({"parameter": [parameter,]})

    mock_requests_get.assert_called_once_with(
        client.cassandra_base_url + "quantum/timeseries", {"parameter": [parameter]}
    )
    assert json_data["query"]["parameterCode"] == parameter

    dataset_size = json_data["result"]["dataSetSize"]
    assert len(json_data["result"]["data"]) == dataset_size
