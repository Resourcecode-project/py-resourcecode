#!/usr/bin/env python3
# coding: utf-8

# Copyright 2020-2022 IFREMER (Brest, FRANCE), all rights reserved.
# contact -- mailto:nicolas.raillard@ifremer.fr
#
# This file is part of Resourcecode.
# Written by Logilab SA (contact@logilab.fr)
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

import plotly.graph_objects as go
import plotly.io as pio

pio.templates["resourcecode"] = go.layout.Template(
    layout_annotations=[
        dict(
            name="draft watermark",
            text="Figure made with resourcecode",
            opacity=0.7,
            font=dict(color="black", size=15),
            xref="paper",
            yref="paper",
            x=1.0,
            xanchor="right",
            y=0.1,
            showarrow=False,
        )
    ]
)
