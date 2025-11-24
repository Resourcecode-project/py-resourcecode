# coding: utf-8
"""
Visualize the database configuration: nodes, bathymetry...
==========================================================
"""
import resourcecode
import numpy as np
import matplotlib.pyplot as plot
import matplotlib.tri as mtri
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable

plot.rcParams["figure.dpi"] = 400
# %%
# Select a node and plot the mesh around
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# Below is an extract of the nodes locations and characteristics.
resourcecode.data.get_grid_field()
# %%
# One can also obtain the location of the points where the full 2D spectral data is available using
# `resourcecode.get_grid_spec()` function
resourcecode.get_grid_spec()
# %%
# Usually, we know the coordinates of the point we want to look at.
# It is possible to find the closest node from this location, using the
# following function. It return a vector of dimension two, with the node number and the distance from
# the requested location (in meters).

# We select the closest node from given coordinates
selected_node = resourcecode.data.get_closest_point(
    latitude=48.3026514, longitude=-4.6861533
)
selected_node

# %%
# Once the node is selected, it is possible to print a map of the area.

lat_min, lat_max = 47.75, 48.75
lon_min, lon_max = -5.25, -4.25

nodes = resourcecode.data.get_grid_field().query(
    f"latitude <= {lat_max} and latitude >= {lat_min} and longitude > {lon_min} and longitude < {lon_max}"
)
spec = resourcecode.get_grid_spec().query(
    f"latitude <= {lat_max} and latitude >= {lat_min} and longitude > {lon_min} and longitude < {lon_max}"
)
coast = resourcecode.data.get_coastline().query(
    f"latitude <= {lat_max} and latitude >= {lat_min} and longitude > {lon_min} and longitude < {lon_max}"
)
islands = resourcecode.data.get_islands().query(
    f"latitude <= {lat_max} and latitude >= {lat_min} and longitude > {lon_min} and longitude < {lon_max}"
)
plot.figure(figsize=(10, 10))
plot.scatter(nodes.longitude, nodes.latitude, s=1, label="Nodes")
plot.scatter(spec.longitude, spec.latitude, s=2, color="orange", label="Spectral grid")
plot.ylim(lat_min, lat_max)
plot.xlim(lon_min, lon_max)
plot.plot(coast.longitude, coast.latitude, color="black")
classes = list(islands.ID.unique())
for c in classes:
    df2 = islands.loc[islands["ID"] == c]
    plot.plot(df2.longitude, df2.latitude, color="black")
plot.scatter(
    nodes[nodes.node == selected_node[0]].longitude,
    nodes[nodes.node == selected_node[0]].latitude,
    s=3,
    color="red",
    label="Selected point",
)
plot.legend()
plot.show()
# %%
#
# ####################################################################
#
# Plot of bathymetry next to the selected point
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# The data included in the toolbox alows to easily map the depth anywhere on the covered area. The following piece
# of code shows and example of such a map.

# Importing the data for plotting
tri = (
    resourcecode.get_triangles().to_numpy() - 1
)  # The '-1' is due to the Zero-based numbering of python
field_mesh = resourcecode.data.get_grid_field().to_numpy()
triang = mtri.Triangulation(field_mesh[:, 1], field_mesh[:, 2], tri)

plotted_nodes = (
    (field_mesh[:, 1] <= lon_max)
    & (field_mesh[:, 1] >= lon_min)
    & (field_mesh[:, 2] <= lat_max)
    & (field_mesh[:, 2] >= lat_min)
)

s = field_mesh[:, 3]
s[np.isnan(s)] = 0  # Due to missing values in bathy

fig = plot.figure(figsize=(10, 10))

ax0 = fig.add_subplot(111, aspect="equal")

plot.ylim(lat_min, lat_max)
plot.xlim(lon_min, lon_max)
SC = ax0.tripcolor(triang, s, shading="gouraud")
SC.set_clim(min(s[plotted_nodes]), max(s[plotted_nodes]))
# Plot selected location
plot.scatter(
    nodes[nodes.node == selected_node[0]].longitude,
    nodes[nodes.node == selected_node[0]].latitude,
    s=3,
    color="red",
    label="Selected point",
)
# Add coastlines and islands
plot.plot(coast.longitude, coast.latitude, color="black")
classes = list(islands.ID.unique())
for c in classes:
    df2 = islands.loc[islands["ID"] == c]
    plot.plot(df2.longitude, df2.latitude, color="black")

# Colorbar.
the_divider = make_axes_locatable(ax0)
color_axis = the_divider.append_axes("right", size="5%", pad=0.1)
cbar = plot.colorbar(SC, cax=color_axis)
cbar.set_label("Depth (m)", fontsize=18)
plot.show()
