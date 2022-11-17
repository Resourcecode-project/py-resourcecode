# coding: utf-8
"""
Use-case example of the Operational Planning module
===================================================
"""
import calendar
import plotly.graph_objects as go

from resourcecode import Client
from resourcecode.opsplanning import ww_calc, wwmonstats, olmonstats, oplen_calc

# %%
# Introduction to Operational Planning module
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# In this page, we will present some of the functionalities offered by the toolbox
# for operational planning and weather windows computations.
# Here, we will deal with the computation of empirical weather windows only, directly from the time series.
# The examples are given using the Resourcecode data,
# but of course any other data source can be used, e.g. in-situ data.
#
# In addition, a demonstration tool based on this module can be accessed on
# the Resourcode Tools `web page <https://resourcecode.ifremer.fr/tools>`_.

client = Client()
percentiles = [0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]
MONTH_NAMES = list(calendar.month_name)

# %%
# Data extraction
# ^^^^^^^^^^^^^^^
#
# We have selected a location next to Ushant island, node number `36855`

data = client.get_dataframe_from_url(
    "https://resourcecode.ifremer.fr/explore?pointId=136855", parameters=("hs", "tp")
)

# %%
# Weather windows
# ^^^^^^^^^^^^^^^
#
# In this module weather window is defined as uninterrupted window of given length,
# when the operational criteria are met.
# The main deliverable is the number (count) of weather windows (and various statistics around the number).
# The number of weather windows for a given period of time can be considered back-to-back
# (next window is considered after the end of pervious window)
# or for any timestamp - every timestamp is considered as potential start of a weather window.
#
# Operational criteria
# --------------------
#
# We assume here that the constraints are in terms of :math:`H_s` and :math:`T_p`, although
# any constraint can be used, as soon as the data is available (e.g. wind or current speed, etc.).
# We also need to define the length of the weather windows needed, defined in hours.

criteria = "hs < 1.8 and tp < 9"
winlen = 3
data_matching_criteria = data.query(criteria)

# %%
# Computation of weather windows
# ------------------------------
#
# Next, takes place the most important part of the module:
# computing the effective weather windows, and then compute monthly statistics.

windetect = ww_calc(data_matching_criteria, winlen=winlen, concurrent_windows=False)
results = wwmonstats(windetect)
stats = results.describe(percentiles=percentiles).drop(["count", "std"]).transpose()

# %%
# Plotting the monthly statistics
# -------------------------------
#
# Lastly, we can produce some plots of the `stats` matrix.

fig = go.Figure()
for colname in stats.columns:
    fig.add_trace(
        go.Scatter(
            x=[MONTH_NAMES[i] for i in stats.index],
            y=stats[colname],
            name=colname,
            legendgroup="by_month",
        )
    )

fig.update_xaxes(title_text="Month")
fig.update_yaxes(title_text="Number of Weather Window")
fig.update_layout(
    height=800,
    legend_tracegroupgap=130,
    title="Monthly statistics of number of weather window (Concurrent)",
)

# %%
# Operational planning
# ^^^^^^^^^^^^^^^^^^^^
#
#
# The operational length is how long will it take to carry out the operation of given nominal length,
# when taking into account weather downtime.
# Operational length is provided in units of time. When calculating the length,
# operations can be considered critical or non-critical.
# With critical operations, the full operations have to restart if criteria is exceeded.
# With non-critical operations, they can be paused for the bad weather
# and continued once the conditions meet the criteria.
#
# Operational criteria
# --------------------

criteria = "hs < 1.8 and tp < 9"
oplen = 12
critical_operation = False

# %%
# Computation of operation durations
# ----------------------------------
#
# Once the criteria are defined, we can proceed to the estimation,
# and finally produce visual exploration of the durations.

oplendetect = oplen_calc(data_matching_criteria, oplen, critical_operation)
results = olmonstats(oplendetect)
stats = results.describe(percentiles=percentiles).drop(["count", "std"]).transpose()

fig = go.Figure()
for colname in stats.columns:
    fig.add_trace(
        go.Scatter(
            x=[MONTH_NAMES[i] for i in stats.index],
            y=stats[colname],
            name=colname,
            legendgroup="by_month",
        ),
    )

fig.update_xaxes(title_text="Month")
fig.update_yaxes(title_text="Length of operations")
fig.update_layout(
    height=800,
    legend_tracegroupgap=130,
    title="Monthly statistics of length of operations (non-critical operations)",
)