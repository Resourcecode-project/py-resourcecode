# coding: utf-8

# Copyright 2020-2022 IFREMER (Brest, FRANCE), all rights reserved.
# contact -- mailto:nicolas.raillard@ifremer.fr
#
# This file is part of Resourcecode.
# Written by Logilab SA (contact@logilab.fr)
#
# Resourcecode is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3.0 of the License, or (at your option)
# any later version.
#
# Resourcecode is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with Resourcecode. If not, see <https://www.gnu.org/licenses/>.

import sys
import json
from urllib.parse import urljoin, urlparse, parse_qs, unquote_plus
from datetime import datetime
from typing import Iterable, Union, Optional

import requests
import pandas as pd
import numpy as np

from resourcecode.utils import get_config
from resourcecode.data import get_variables, get_grid_field
from resourcecode.exceptions import BadParameterError, BadPointIdError


class Client:
    """Define a client to query data from the cassandra database

    Example
    -------

    .. doctest::

        >>> from resourcecode import Client
        >>> client = Client()
        >>> data = client.get_dataframe_from_url(
        ...     "https://resourcecode.ifremer.fr/explore/?pointId=42"
        ... )
        >>> data = client.get_dataframe(
        ...     pointId=42,
        ...     startDateTime="2017-01-01T00:53:20",
        ...     endDateTime="2017-03-19T07:06:40",
        ...     parameters=["hs", "fp"],
        ... )
        >>>
    """

    def __init__(self):
        self.config = get_config()
        self.possible_parameters = set(get_variables().name)
        self.possible_points_id = set(get_grid_field().node)

    @property
    def cassandra_base_url(self):
        return self.config.get("default", "cassandra-base-url")

    def get_dataframe(
        self,
        pointId: int,
        startDateTime: Optional[Union[str, datetime, int]] = None,
        endDateTime: Optional[Union[str, datetime, int]] = None,
        parameters: Iterable[str] = ("hs",),
    ) -> pd.DataFrame:
        """Get a pandas dataframe of the data described by the criteria

        Parameters
        ----------

        pointId: int
            the id of the point to get data from
        startDateTime: optional datetime or string (date in isoformat) or int (timestamp)
            the start of the selection.
            if not given, the oldest possible value will be used.
        endDateTime: optional datetime or string (date in isoformat) or int (timestamp)
            the end of the selelection.
            if not given, the most recent possible value will be used.
        parameters: list of string
            the parameters to retrieve

        Return
        ------

        A pandas dataframe with a datetime index, from `startDateTime` to
        `endDateTime`, and with one column per parameter.
        """

        if isinstance(startDateTime, str):
            startDateTime = datetime.fromisoformat(startDateTime)
        if isinstance(startDateTime, datetime):
            startDateTime = int(startDateTime.timestamp())

        if isinstance(endDateTime, str):
            endDateTime = datetime.fromisoformat(endDateTime)
        if isinstance(endDateTime, datetime):
            endDateTime = int(endDateTime.timestamp())

        criteria = {
            "node": pointId,
            "start": startDateTime,
            "end": endDateTime,
            "parameters": parameters,
        }

        return self.get_dataframe_from_criteria(criteria)

    def get_dataframe_from_url(
        self, selection_url: str, parameters: Iterable[str] = ("hs",)
    ) -> pd.DataFrame:
        """Get the pandas dataframe of the data described by the url

        Parameters
        ----------
        selection_url: string
            the URL of the selection in the resource code web application
        parameters: list of string
            the parameters to retrieve

        Return
        ------

        A pandas dataframe with a datetime index, from `startDateTime` to
        `endDateTime`, and with one column per parameter.
        """

        search_parameters = parse_qs(urlparse(unquote_plus(selection_url)).query)
        if not search_parameters:
            raise ValueError("no criteria found in the url")

        criteria = {
            "node": int(search_parameters["pointId"][0]),
            "parameter": parameters,
        }

        if "startDateTime" in search_parameters:
            start = search_parameters["startDateTime"][0].rstrip("Z")
            criteria["start"] = int(datetime.fromisoformat(start).timestamp())

        if "endDateTime" in search_parameters:
            end = search_parameters["endDateTime"][0].rstrip("Z")
            criteria["end"] = int(datetime.fromisoformat(end).timestamp())

        return self.get_dataframe_from_criteria(criteria)

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

        min_date = self.config.get("default", "min-start-date")
        max_date = datetime.today().isoformat()
        default_criteria = {
            "node": 1,
            "start": int(datetime.fromisoformat(min_date).timestamp()),
            "end": int(datetime.fromisoformat(max_date).timestamp()),
        }

        if isinstance(criteria, str):
            parsed_criteria = json.loads(criteria)
        else:
            parsed_criteria = criteria

        # make sure compulsory parameters are present (node, dates) and are not
        # None.
        parsed_criteria = {**default_criteria, **parsed_criteria}

        if "parameters" in parsed_criteria:
            # let's tolerate `parameter` and `parameters`
            parsed_criteria["parameter"] = parsed_criteria["parameters"]

        result_array = None
        parameters = parsed_criteria.get("parameter", ())
        unknown_parameters = set(parameters) - self.possible_parameters
        if unknown_parameters:
            raise BadParameterError(
                f"{','.join(unknown_parameters)} parameter(s) is/are unknown. "
                "Please have to look to `resourcecode.data.get_variables()`, "
                "to get the accepted parameters."
            )

        try:
            node_id = int(parsed_criteria["node"])
        except ValueError:  # failed to convert node to an integer
            raise BadPointIdError(
                "Point Id must be an integer, can not be "
                f"{parsed_criteria['node']!r}"
            )
        else:
            if node_id not in self.possible_points_id:
                raise BadPointIdError(
                    f"{parsed_criteria['node']} is an unknown pointId."
                )

        # Cassandra database start indexing at 1, so decrement node
        parsed_criteria["node"] = parsed_criteria["node"] - 1

        for parameter in parsed_criteria.get("parameter", ()):
            # we assume that multiple parameters can be given.
            # for each parameter, we make a query and we concatenate all the
            # responses.

            # tp is not a real parameter. it is equal to 1/fp.
            single_parameter = parameter.lower()
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
                result_array = np.column_stack((result_array, parameter_array[:, 1]))  # type: ignore
            except ValueError:
                result_array = parameter_array
                index_array = parameter_array[:, 0]
                mask_index_nan = np.isnan(index_array)
            except Exception:
                if raw_data["query"]["dataSetSize"] == 0:
                    print(
                        "It appears the API failed to returned the expected values. "
                        "You may try to recall the function in a few moment.",
                        file=sys.stderr,
                    )
                    return pd.DataFrame()
                raise

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
            index=pd.to_datetime(index_array.astype(np.int64), unit="ms"),
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
