from dash import html, dcc
from typing import List
from components import Traffic


def camera_view(sources: List[str]):
    layout = html.Div(
        id="camera-view",
    )
    children = []
    for source in sources:
        children.append(
            html.Div(
                className="card mb-3",
                children=[
                    html.Div(
                        className="card-header",
                        children=[
                            html.I(className="fas fa-video mr-2"),
                            html.Span(source),
                        ],
                    ),
                    html.Div(
                        className="card-body",
                        children=[
                            html.Div(
                                className="row",
                                children=[
                                    html.Div(
                                        className="col-lg-6 col-md-6 col-sm-6 col-xs-6",
                                        children=[
                                            html.Img(
                                                src=source,
                                                className="img-fluid",  # Make the image responsive
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        className="col-lg-6 col-md-6 col-sm-6 col-xs-6",
                                        children=[
                                            Traffic.traffic_status(source),
                                            Traffic.traffic_graph(source),
                                        ],
                                    ),
                                ],
                            ),
                            html.H5(
                                f"Camera {source}",
                                className="card-title",
                            ),  # Apply card-title class
                            html.P(
                                f"Camera {source} is currently streaming",
                            ),  # Apply p class
                        ],
                    ),
                ],
            )
        )
    layout.children = children
    return layout
