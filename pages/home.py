import plotly.express as px
from dash import Input, Output, no_update, State, Patch, MATCH, ALL, callback
from dash.dependencies import Input, Output
from dash import html, dcc, callback
import dash
import yaml
import json
import numpy as np
from coordinate import coordinate_extractor
from components import CameraView, Traffic, Zone
from processor import video_processor_manager as processor

COUNTER_ZONE: np.ndarray = None
ZONES = []
CONFIGURATIONS = {"zones": ZONES, "counter_zone": COUNTER_ZONE}


config_px = {
    "modeBarButtonsToAdd": [
        "drawclosedpath",
        "eraseshape",
    ]
}

layout = html.Div(
    className="container py-5",  # Apply Bootstrap container class and padding
    children=[
        CameraView.camera_view(["/video_feed"]),
        # dcc.Interval(id="interval-component", interval=1 * 2000, n_intervals=0),
        html.Div(
            className="card mb-4",
            children=[
                html.Div(
                    className="card-body",
                    children=[
                        html.H5("Zones", className="card-title"),
                        html.P("Add zones to the video"),
                        html.Div(
                            className="form-group mt-2",
                            children=[
                                html.Label("Select Zone Type:"),
                                dcc.Dropdown(
                                    id="zone-type-dropdown",
                                    options=[
                                        {
                                            "label": "Counter Zone",
                                            "value": "counter_zone",
                                        },
                                        {"label": "Entry Zone", "value": "entry_zone"},
                                    ],
                                    value="counter_zone",
                                ),
                            ],
                        ),
                        html.Button(
                            "Load Zone from Config",
                            id="load-zone-button",
                            className="btn btn-primary mt-2",
                            n_clicks=0,
                        ),
                        html.Button(
                            "Add Zone",
                            id="add-zone-button",
                            className="btn btn-primary mt-2",
                            n_clicks=0,
                        ),
                        html.Div(id="zone-form", className="mt-2", children=[]),
                    ],
                ),
            ],
        ),
    ],
)


@callback(
    Output("traffic-status", "children"),
    Input("traffic-status-interval", "n_intervals"),
    prevent_initial_call=True,
)
def update_traffic_status(n_intervals):
    children = []
    if processor.video is None:
        return no_update
    for zone in processor.video.detections_manager.counter_time:
        children.append(
            html.Div(
                className="row",
                children=[
                    html.Div(
                        className="col-md-3",
                        children=[
                            html.Label(f"Zone {zone}"),
                        ],
                    ),
                    html.Div(
                        className="col-md-3",
                        children=[
                            html.Label(
                                f"Average Time: {processor.video.detections_manager.counter_time[zone]['average_time']}/s"
                            ),
                        ],
                    ),
                    html.Div(
                        className="col-md-3",
                        children=[
                            html.Label(
                                f"Real Waiting Time: {processor.video.detections_manager.counter_time[zone]['real_waiting_time']}/s"
                            ),
                        ],
                    ),
                ],
            )
        )
    return children
