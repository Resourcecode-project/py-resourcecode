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

import json
from unittest import mock
from datetime import datetime

import pytest
import pandas as pd

import resourcecode
from resourcecode.exceptions import BadPointIdError, BadParameterError

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
    start_date = parameters.get("start")
    end_date = parameters.get("end")
    data_path = DATA_DIR / f"timeseries_{parameter}.json"

    if not data_path.exists():
        mocked_response.ok = False
        return mocked_response

    with open(data_path) as fobj:
        data = json.load(fobj)
        records = []
        # mock cassandra:
        # if date is None, return it.
        # filter dates that are not between start and end dates
        for date, value in data["result"]["data"]:
            # start_date and end_date must be multiplied by 1e3, because
            # cassandra returns milliseconds
            if date is not None and (
                start_date is not None and date < start_date * 1e3
            ):
                continue

            if date and end_date is not None and date > end_date * 1e3:
                break

            records.append([date, value])

        data["result"]["data"] = records
        mocked_response.json.return_value = data

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


def test_unknown_parameters_and_pointid():
    client = resourcecode.Client()

    with mock.patch("requests.get", side_effect=mock_requests_get_raw_data):
        assert not client.get_dataframe(
            pointId=1,
            parameters=[
                "hs",
            ],
        ).empty

        with pytest.raises(BadPointIdError):
            client.get_dataframe(
                pointId="abc",
                parameters=[
                    "hs",
                ],
            )

        with pytest.raises(BadPointIdError):
            client.get_dataframe(
                pointId=328031,
                parameters=[
                    "hs",
                ],
            )

        with pytest.raises(BadParameterError) as excinfo:
            # hs_max does not exist
            client.get_dataframe(
                pointId=1,
                parameters=[
                    "hs_max",
                ],
            )
        assert "hs_max" in str(excinfo.value)


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


def test_different_available_methods_to_get_data(client):
    start_date = "2017-01-01 00:00:00"
    end_date = "2017-01-10 13:00:00"

    data_from_critera = client.get_dataframe_from_criteria(
        {
            "node": 42,
            "start": datetime.fromisoformat(start_date).timestamp(),
            "end": datetime.fromisoformat(end_date).timestamp(),
            "parameter": ["tp"],
        }
    )
    data_from_url = client.get_dataframe_from_url(
        f"https://fake-app.fr/?pointId=42&startDateTime={start_date}&endDateTime={end_date}",
        parameters=("tp",),
    )
    data_from_args = client.get_dataframe(
        pointId=42,
        startDateTime=start_date,
        endDateTime=end_date.replace("23", "22"),
        parameters=("tp",),
    )

    assert (data_from_url == data_from_critera).all().bool()
    assert (data_from_args == data_from_critera).all().bool()
