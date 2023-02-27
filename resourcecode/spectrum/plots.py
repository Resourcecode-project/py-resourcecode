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

import numpy as np
import pandas as pd
import xarray
import matplotlib.pyplot as plt
from matplotlib.projections.polar import PolarAxes

from resourcecode.spectrum import (
    raw_compute_parameters_from_2D_spectrum,
    raw_compute_parameters_from_1D_spectrum,
)


def plot_2D_spectrum(
    data: xarray.Dataset,
    time: int,
    sea_state: bool = True,
    normalize: bool = True,
    cut_off: float = 0.4,
    trim: float = 0.01,
) -> plt.Figure:
    """Plot the 2D spectrum at a specific time

    Parameters
    ----------

    data:
        Data with the time series of wave spectrum (xarray.Dataset)
    time:
        Time index to plot
    sea_state:
        Should the sea_state parameters be computed and included in the plot ?
    normalize:
        Should the spectrum be normalized (at a max value of 1) ?
    cut_off:
        cut-off frequency above with the spectrum is not plotted
    trim:
        removes the values of the spectral density lower than this value
    Returns
    -------

    fig: figure containing the spectrum
    """
    if time > data.time.size:
        raise IndexError(f"time is out the length of the Dataset: {data.time.size}")
    else:
        # Compute the frequency and direction vectors: the must cover the size of Ef plus 1
        freq = np.append(data.frequency1.to_numpy(), data.frequency2[-1].to_numpy())
        direction = np.append(data.sortby("direction").direction.to_numpy(), 360.0)
        # Create the new figure
        fig = plt.figure(
            figsize=(10, 10),
            dpi=400,
            facecolor="w",
            edgecolor="w",
        )
        rect = [0.1, 0.1, 0.8, 0.8]

        # Switch to polar coordinates
        ax = PolarAxes(fig, rect)
        fig.add_axes(ax)
        ax.set_theta_direction(-1)  # Rotate clockwize
        ax.set_theta_offset(np.pi / 2.0)  # origion to the North

        # Gather the table of wave spectrum
        Ef = data.sortby("direction").Ef[time, :, :].to_numpy()

        # Compute the sea_state parameters if requested
        if sea_state:
            params = raw_compute_parameters_from_2D_spectrum(
                Ef.transpose(),
                vdir=direction[:-1],
                freq=freq[:-1],
                depth=float(data.dpt[time]),
            )
            sea_state_str = "\n".join(
                [
                    f"Hs: {params.Hm0:.2f}m",
                    f"Tp: {params.Tp:.2f}s",
                    f"Mean direction at Tp: {params.Thetapm:.2f}°",
                    f"Directionnal spreading: {params.Spr:.2f}°",
                    f"Wind speed: {float(data.wnd[time]):.2f}m/s",
                    f"\u27F6, wind direction: {float(data.wnddir[time]):.2f}°",
                ]
            )

        # Normalize the wave spectrum to a max of one if needed
        if normalize:
            Ef = Ef / Ef.max()

        Ef[Ef < trim] = np.nan

        ax.grid(False)  # Just to remove warning from 'pcolormesh', add it back latter

        # Actual plot of the image
        pt = ax.pcolormesh(
            np.radians((direction + 180) % 360),  # Switch direction from/to
            freq,
            Ef,
            edgecolors="face",  # for a better output
            cmap="PuBu",
        )
        ax.set_ylim([0, cut_off])  # Zoom in the area where there are interesting things
        ax.set_rlabel_position(89)  # Rotate a little bit the legend to avoid colliding

        # Add horizontal axis label
        plt.annotate(r"f ($Hz$)", xy=(np.pi / 2 + 0.1, cut_off / 2))

        ax.grid(True)  # Add back the grid

        # Plot the sea state characteristics if requested
        if sea_state:
            plt.annotate(
                sea_state_str,
                [np.pi / 3 - 0.1, cut_off * 1.05],
                annotation_clip=False,
            )
        # Construct the title from the attributes of the Dataset
        title = "\n".join(
            [
                f"Wave directional spectrum at point {data.attrs['product_name'].split('_')[1].split('-')[3]}",
                f"({data.longitude[time].data:.2f}°W,{data.latitude[time].data:.2f}°N)",
                f"on {pd.to_datetime(data.time[time].data)}",
            ]
        )
        plt.title(title)

        # Add the wind arrow
        if sea_state:
            plt.annotate(
                "",
                xy=(0, 0),
                xytext=(np.radians(float(data.wnddir[time])), 0.05),
                arrowprops=dict(arrowstyle="->"),
            )

        cbar = fig.colorbar(pt, orientation="horizontal", pad=0.05)
        if normalize:
            cbar.set_label("Normalized spectrum value")
        else:
            cbar.set_label("Spectrum value (m^2/Hz)")

        # Add the resourcecode caption
        plt.annotate(
            "\nSource: Resourcecode hindcast database\nresourcecode.ifremer.fr",
            xy=(7 / 8 * np.pi, 1.1 * cut_off),
            annotation_clip=False,
        )

    return ax


def plot_1D_spectrum(
    data: xarray.Dataset,
    time: int,
    sea_state: bool = True,
) -> plt.axis:
    """Plot the 1D spectrum at a specific time

    Parameters
    ----------

    data:
        Data with the time series of wave spectrum (xarray.Dataset)
    time:
        Time index to plot
    sea_state:
        Should the sea_state parameters included in the plot ?
    Returns
    -------

    fig: figure containing the spectrum
    """
    if time > data.time.size:
        raise IndexError(f"time is out the length of the Dataset: {data.time.size}")
    else:
        # Create the new figure
        fig = plt.figure(
            figsize=(8, 6),
            dpi=400,
            facecolor="w",
            edgecolor="w",
        )
        rect = [0.1, 0.1, 0.8, 0.8]

        # Switch to polar coordinates
        ax = PolarAxes(fig, rect)
        fig.add_axes(ax)
        plt.plot(data.frequency.to_numpy(), data.ef[time, :].to_numpy())
        plt.xlabel(r"f ($Hz$)")
        plt.ylabel(r"Wave spectral density ($m^2 s$)")
        plt.ylim(bottom=0)
        plt.xlim(left=0, right=max(data.frequency.data))
        _, top = plt.ylim()

        # Compute the sea-state parameters from the 1D spectrum to be consistent
        # with the 2D case
        params = raw_compute_parameters_from_1D_spectrum(
            data.ef[time, :].to_numpy(),
            freq=data.frequency.to_numpy(),
            depth=data.dpt[time].data,
        )

        if sea_state:
            sea_state_str = "\n".join(
                [
                    f"Hs: {params.Hm0:.2f}m",
                    f"Tp: {params.Tp:.2f}s",
                    f"Mean direction at Tp: {float(data.th1p[time]):.2f}°",
                    f"Directionnal spreading: {float(data.sth1p[time]):.2f}°",
                    f"Wind speed: {float(data.wnd[time]):.2f}m/s",
                    f"Wind direction: {float(data.wnddir[time]):.2f}°",
                    "\nSource: Resourcecode hindcast database",
                    "resourcecode.ifremer.fr",
                ]
            )
        else:
            sea_state_str = "\n".join(
                [
                    "\nSource: Resourcecode hindcast database",
                    "resourcecode.ifremer.fr",
                ]
            )
        plt.annotate(
            sea_state_str,
            [0.5, top / 2],
            [0.5, top / 2],
            annotation_clip=False,
        )
        title = " ".join(
            [
                "Wave frequency spectrum at\n",
                f"point {data.attrs['product_name'].split('_')[1].split('-')[3]}",
                f"({data.longitude[time].data:.2f}°W,{data.latitude[time].data:.2f}°N)",
                f"on {pd.to_datetime(data.time[time].data)}",
            ]
        )
        plt.title(title)
        return fig
