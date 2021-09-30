Helpers to get embedded data
============================

.. automodule:: resourcecode.data
    :members:

Import/export helpers
=====================

When the :py:mod:`resourcecode` is loaded, all pandas DataFrame
automatically have a :py:meth:`to_netcdf` method, and the pandas module has a
:py:func:`read_netcdf` function.

For instance::

    import pandas as pd

    # load the module to provide pandas the `read_netcdf` and `to_netcdf`
    # functions
    import resourcecode

    dataframe = pd.read_netcdf("path/to/my_data.nc")

    # to some work on dataframe

    dataframe.to_netcdf("path/to/new_data.nc")


If you need custom options to import/export netcdf files, one could use
functions from `xarray
<https://xarray.pydata.org/en/stable/generated/xarray.Dataset.to_netcdf.html#xarray.Dataset.to_netcdf>`_
for instance.


.. automodule:: resourcecode.io
    :members:

