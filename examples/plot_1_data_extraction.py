# coding: utf-8
"""
Extract some time-series from the database and analysis
==========================================================
"""
import resourcecode
import resourcecode.spectrum
import matplotlib.pyplot as plot

plot.rcParams["figure.dpi"] = 400

# %%
# Node selection and data extraction
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# Below, we will look for data next to the location of interest, located in the vicinity of Brest Bay.
# We will look at the time-series data and also some spectral data
#
selected_node = resourcecode.data.get_closest_point(
    latitude=48.3026514, longitude=-4.6861533
)
selected_node
# %%
selected_specPoint = resourcecode.data.get_closest_station(
    latitude=48.3026514, longitude=-4.6861533
)
selected_specPoint

# %%
# Extraction of data from the Hindcast database
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# Sea-state parameters extraction and helpers from the toolbox
# ------------------------------------------------------------
#
# Once the node is selected, it is possible to retrieve the data from the Cassandra database using the
# commands below. It is also possible to select which variables to retrieve.
# The list of available variables can be obtained using the `get_variables` method.
# We study here the following variables:
#
#  - :math:`H_s`, the significant wave height;
#  - :math:`T_p` the peak period;
#  - :math:`D_p` the direction at peak frequency;
#  - The energy flux :math:`CgE`;
#  - zonal and meridional velocity components of wind;
#
# For this example, we have selectedonly year 2010.

client = resourcecode.Client()
data = client.get_dataframe(
    pointId=selected_node[0],
    startDateTime="2010-01-01T01:00:00",
    endDateTime="2011-01-01T00:00:00",
    parameters=("hs", "uwnd", "vwnd", "t02", "tp", "dp", "cge"),
)
data.head()

# %%
# With the toolbox, is is possible to convert zonal and meridional velocity components of wind the the more
# convenient Intensity-direction variables.

data["wspd"], data["wdir"] = resourcecode.utils.zmcomp2metconv(data.uwnd, data.vwnd)

# %%
# The figure below is an example of the histograme of the variables that can be
# extracted from the database. :math:`H_s`,:math:`T_p`, :math:`W_s` and :math:`CgE` are
# shown here with the wind and wave directions, but the code can be changed to plot any
# of the available variables in the Hindcast database.

data[["hs", "tp", "cge", "wspd", "dp", "wdir"]].hist(bins=15, figsize=[16, 8])
plot.tight_layout()

# %%
# Spectral data extraction and computation of sea-state parameters
# ----------------------------------------------------------------
#
# The toolbox also offers the possibility to download the spectral data from the coarser 'SPEC' grid,
# corresponding to the orange dots of the web portal. This is possible thanks to the `get_2D_spectrum` and
# `get_1D_spectrum` from the *spectrum* module. An example is shown below:

spec = resourcecode.spectrum.get_2D_spectrum(
    selected_specPoint[0], years=["2010"], months=["01"]
)

# %%
# And we offers function to represent the spectral data (for 2D and 1D, even if only the 2D is shown here)

resourcecode.spectrum.plot_2D_spectrum(spec, 1)
plot.show()

# %%
# Among the functionalities of the toolbox, it is possible to compute the sea-state parameters from spectral data. Small
# discrepancies can be found between the Hindcast sea-state parameters and the one computed with the toolbox.

parameters_df = resourcecode.spectrum.compute_parameters_from_2D_spectrum(
    spec, use_depth=True
)
parameters_df.head()
