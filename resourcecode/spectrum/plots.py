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
import matplotlib.pyplot as plt

from resourcecode.spectrum import (
    compute_parameters_from_2D_spectrum,
)


def plot_2D_spectrum(data, time):

    if time > data.time.size:
        raise IndexError(f"time is out the length of the Dataset: {data.time.size}")
    else:
        freq = np.append(data.frequency1.to_numpy(), data.frequency2[-1].to_numpy())
        direction = np.append(data.sortby("direction").direction.to_numpy(), 360.0)
        plt.clf()
        fig = plt.figure(figsize=[12, 12])
        ax = fig.add_axes([0, 0, 1.1, 1.1], polar=True)
        Ef = data.sortby("direction").Ef[time, :, :].to_numpy()

        params = compute_parameters_from_2D_spectrum(
            Ef, vdir=direction[:-1], freq=freq[:-1], depth=float(data.dpt[time])
        )
        Ef = Ef / Ef.max()
        ax.grid(False)  # Just to remove warning from 'pcolormesh', add it back latter
        pt = ax.pcolormesh(
            np.radians((direction + 180) % 360),
            freq,
            Ef,
            edgecolors="face",
            cmap="PuBu",
        )
        ax.set_ylim([0, 0.4])
        ax.set_rlabel_position(0)
        ax.set_xlabel("f (Hs)")
        ax.grid(True)
        sea_state = "\n".join(
            [
                f"Hs: {params.Hm0:.2f}m",
                f"Tp: {params.Tp:.2f}s",
                f"Mean direction at Tp: {params.Thetapm:.2f}°",
                f"Directionnal spreading: {params.Spr:.2f}°",
                f"Wind speed: {float(data.wnd[time]):.2f}m/s",
            ]
        )
        plt.annotate(
            sea_state,
            [np.pi / 3 - 0.1, 0.41],
            annotation_clip=False,
        )
        title = '\n'.join(
            [
            "Wave directional spectrum at\n",
            f"point {data.attrs['product_name'].split('_')[1].split('-')[3]}",
            f"({data.longitude[time].data:.2f}°W,{data.latitude[time].data:.2f}°N)",
            f"on {pd.to_datetime(data.time[time].data)}",
            ]
        )
        plt.title(title)
        plt.annotate(
            "",
            xy=(0, 0),
            xytext=(np.radians(float(data.wnddir[time])), 0.05),
            arrowprops=dict(arrowstyle="->"),
        )
        cbar = fig.colorbar(pt, orientation="horizontal", pad=0.05)
        cbar.set_label("Normalized spectrum value")
        plt.annotate(
            "\nSource: Resourcecode hindcast database\nresourcecode.ifremer.fr",
            xy=(-np.pi / 3, 0.47),
            annotation_clip=False,
        )
        return fig
