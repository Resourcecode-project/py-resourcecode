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

from resourcecode import (
    get_coastline,
    get_grid_field,
    get_grid_spec,
    get_islands,
    get_triangles,
    get_variables,
)


def _check_loader(loader, expected_columns):
    """Assert that the loader:

    - return a non empty data frame
    - the columns are the expected ones
    - the columns names are found in the loader docstring
    """

    data = loader()
    assert len(data) > 0
    assert (data.columns == expected_columns).all(), data.columns
    for column in data.columns:
        assert column in loader.__doc__


def test_load_data():
    """Assert static data are properly loaded"""

    _check_loader(get_coastline, ["longitude", "latitude", "depth"])
    _check_loader(get_grid_field, ["node", "longitude", "latitude", "depth", "d50"])
    _check_loader(get_grid_spec, ["longitude", "latitude", "name", "depth", "d50"])
    _check_loader(get_islands, ["longitude", "latitude", "depth", "ID"])
    _check_loader(get_triangles, ["Corner 1", "Corner 2", "Corner 3"])
    _check_loader(get_variables, ["name", "longname", "unit"])
