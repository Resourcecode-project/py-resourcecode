Helpers to get embedded data
============================

.. automodule:: resourcecode.data
    :members:

Import/export helpers
=====================

When the :py:mod:`resourcecode` is loaded, all pandas DataFrame
automatically have a :py:meth:`to_netcfd` method, and the pandas module has a
:py:func:`read_netcfd` function.

For instance::

    import pandas as pd

    # load the module to provide pandas the `read_netcfd` and `to_netcfd`
    # functions
    import resourcecode

    dataframe = pd.read_netcfd("path/to/my_data.nc")

    # to some work on dataframe

    dataframe.to_netcfd("path/to/new_data.nc")


If you need custom options to import/export netcfd files, one could use
functions from `xarray
<https://xarray.pydata.org/en/stable/generated/xarray.Dataset.to_netcdf.html#xarray.Dataset.to_netcdf>`_
for instance.


.. automodule:: resourcecode.io
    :members:

