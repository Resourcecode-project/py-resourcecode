#!/usr/bin/env python3
# coding: utf-8

from urllib.parse import urljoin

import requests

from resourcecode.utils import get_config


class Client:
    def __init__(self):
        self.config = get_config()

    @property
    def cassandra_base_url(self):
        return self.config.get("default", "cassandra-base-url")

    def _get_rawdata(self, parameters):
        """ return the json of the data described by the parameters

            Parameters
            ----------
            parameters: dict
                the dictionnary of parameters to give to cassandra

            Result
            ------
            result: json
                the json result returned by the cassandra database.
        """
        query_url = urljoin(self.cassandra_base_url, "quantum/timeseries")

        response = requests.get(query_url, parameters)
        if response.ok:
            return response.json()

        raise ValueError(
            "Unable to get a response from the database"
            "(status code = {})".format(response.status_code)
        )
