#!/usr/bin/env python3
# coding: utf-8

from urllib.parse import urljoin
import json
from typing import Union

import requests
import pandas as pd
import numpy as np

from resourcecode.utils import get_config


class Client:
    """Define a client to query data from the cassandra database

    Example
    -------

    >>> from resourcecode import Client
    >>> client = Client()
    >>> data = client.get_dataframe_from_criteria(
    \"""
    {
        "node": 0,
        "start": 1483228400,
        "end": 1489903600,
        "parameter": ["fp", "hs"]
    }
    \""")
    >>>
    """

    def __init__(self):
        self.config = get_config()

    @property
    def cassandra_base_url(self):
        return self.config.get("default", "cassandra-base-url")

    def get_dataframe_from_criteria(self, criteria: Union[str, dict]) -> pd.DataFrame:
        """return the pandas dataframe of the data described by the criteria

        The criteria must be like this:

        .. code-block::

            {
                "node": pointId,  # the point id
                "start": start,   # the timestamp of the beginning of the selection
                                  # in *miliseconds*
                "end": end,       # the timestamp of the end of the selection
                                  # in *miliseconds*
                "parameters": ["hs", "fp"], # the list of parameters to retrieve
            }


        Parameters
        ----------
        criteria: string (json) or dict
            a json-formatted string describing the criteria
            or the criteria as a dictionary

        Return
        ------
        data: a Pandas DataFrame of the selected data
        """

        if isinstance(criteria, str):
            parsed_criteria = json.loads(criteria)
        else:
            parsed_criteria = criteria

        if "parameters" in parsed_criteria:
            # let's tolerate `parameter` and `parameters`
            parsed_criteria["parameter"] = parsed_criteria["parameters"]

        result_array = None
        for parameter in parsed_criteria.get("parameter", ()):
            # we assume that multiple parameters can be given.
            # for each parameter, we make a query and we concatenate all the
            # responses.

            # tp is not a real parameter. it is equal to 1/fp.
            single_parameter = parameter
            if parameter == "tp":
                single_parameter = "fp"
            single_parameter_criteria = {
                **parsed_criteria,
                "parameter": [
                    single_parameter,
                ],
            }
            raw_data = self._get_rawdata_from_criteria(single_parameter_criteria)
            # parameter_array is the time history of the current parameter.
            # it's a 2D array. The first columns is the timestamp, the second
            # one the value of this parameters at the corresponding timestamps.
            parameter_array = np.array(raw_data["result"]["data"], dtype=float)
            if parameter == "tp":
                parameter_array[:, 1] = 1 / parameter_array[:, 1]

            try:
                # concatenate and get ride of the timestamp (already known from
                # the previous iteration)
                result_array = np.column_stack((result_array, parameter_array[:, 1]))
            except ValueError:
                result_array = parameter_array
                index_array = parameter_array[:, 0]
                mask_index_nan = np.isnan(index_array)

            # the index may be incomplete in some cases (when the variable is
            # NaN).
            # let's try to have the more complete index as possible, as the
            # index should be the same for all the variable

            if mask_index_nan.any():
                index_array[mask_index_nan] = parameter_array[mask_index_nan, 0]
                mask_index_nan = np.isnan(index_array)

        if result_array is None:
            raise ValueError("no selection parameter found")

        return pd.DataFrame(
            result_array[:, 1:],
            columns=parsed_criteria["parameter"],
            index=pd.to_datetime(index_array.astype(int), unit="ms"),
        )

    def _get_rawdata_from_criteria(self, single_parameter_criteria):
        """return the json of the data described by the parameters

        Parameters
        ----------
        parameters: dict
            the dictionnary of parameters to give to cassandra

        Result
        ------
        result: json
            the json result returned by the cassandra database.
        """
        query_url = urljoin(self.cassandra_base_url, "api/timeseries")

        response = requests.get(query_url, single_parameter_criteria)
        if response.ok:
            return response.json()

        raise ValueError(
            "Unable to get a response from the database"
            "(status code = {})".format(response.status_code)
        )
