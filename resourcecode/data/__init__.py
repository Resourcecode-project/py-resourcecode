#!/usr/bin/env python3
# coding: utf-8

from functools import partial
from pathlib import Path

import pyarrow.feather as feather

DATA_DIR = Path(__file__).parent

get_coastline = partial(feather.read_feather, DATA_DIR / "coastline.feather")
get_grid_field = partial(feather.read_feather, DATA_DIR / "grid_FIELD.feather")
get_grid_spec = partial(feather.read_feather, DATA_DIR / "grid_SPEC.feather")
get_islands = partial(feather.read_feather, DATA_DIR / "islands.feather")
get_triangles = partial(feather.read_feather, DATA_DIR / "triangles.feather")
get_variables = partial(feather.read_feather, DATA_DIR / "variables.feather")

# those parameters are from the feather.read_feather function
COMMON_PARAMETERS = """\
Parameters
----------
columns : sequence, optional
    Only read a specific set of columns. If not provided, all columns are
    read.
use_threads: bool, default True
    Whether to parallelize reading using multiple threads.
memory_map : boolean, default True
    Use memory mapping when opening file on disk

Returns
-------
df : pandas.DataFrame
"""

get_coastline.__doc__ = f"""\
Return a pandas dataframe describing the costline nodes.

The default returned columns are: longitude, latitude, depth.

{COMMON_PARAMETERS}
"""

get_grid_field.__doc__ = f"""\
Return a pandas dataframe describing the grid field.

The default returned columns are: node, longitude, latitude, depth, d50

{COMMON_PARAMETERS}
"""

get_grid_spec.__doc__ = f"""\
Return a pandas dataframe describing the grid specifications.

The default returned columns are: longitude, latitude, name, depth, d50

{COMMON_PARAMETERS}
"""

get_islands.__doc__ = f"""\
Return a pandas dataframe describing the islands.

The default returned columns are: longitude, latitude, depth, ID

{COMMON_PARAMETERS}
"""

get_triangles.__doc__ = f"""\
Return a pandas dataframe describing the mesh triangles.

The default returned columns are: Corner 1, Corner 2, Corner 3.

{COMMON_PARAMETERS}
"""

get_variables.__doc__ = f"""\
Return a pandas dataframe describing the variables used by the Cassandra
database.

The default returned columns are: name, longname, unit

{COMMON_PARAMETERS}
"""

__all__ = [
    "get_coastlines",
    "get_grid_field",
    "get_grid_spec",
    "get_islands",
    "get_triangles",
    "get_variables",
]
