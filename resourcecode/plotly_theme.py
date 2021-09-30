#!/usr/bin/env python3
# coding: utf-8

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
