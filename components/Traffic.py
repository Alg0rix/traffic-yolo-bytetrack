from dash import html, dcc, callback, MATCH, Input, Output, no_update
from typing import List
from processor import video_processor_manager as processor


def traffic_status(id: str):
    return html.Div(
        className="card mb-3",
        children=[
            html.Div(
                className="card-body",
                children=[
                    html.H5(
                        f"Status: {id}", className="card-title"
                    ),  # Apply card-title class
                    html.Div(
                        id={"type": "traffic-status", "id": id},
                        className="card-text",
                    ),  # Apply p class
                    dcc.Interval(
                        id={"type": "interval-traffic-status", "id": id},
                        interval=2 * 1000,
                        n_intervals=0,
                    ),
                ],
            ),
        ],
    )


def traffic_graph(id: str):
    return html.Div(
        className="card mb-3",
        children=[
            html.Div(
                className="card-body",
                children=[
                    html.H5(
                        f"Graph: {id}", className="card-title"
                    ),  # Apply card-title class
                    html.Div(
                        id={"type": "traffic-graph", "id": id},
                        className="card-text",
                    ),  # Apply p class
                    dcc.Interval(
                        id={"type": "interval-traffic-graph", "id": id},
                        interval=2 * 1000,
                        n_intervals=0,
                    ),
                ],
            ),
        ],
    )


def get_traffic_conclusion(waiting_time):
    if waiting_time >= 0 and waiting_time < 10:
        return "Smooth"
    elif waiting_time >= 10 and waiting_time < 20:
        return "Slow"
    elif waiting_time >= 20 and waiting_time < 30:
        return "Congested"


@callback(
    Output({"type": "traffic-status", "id": MATCH}, "children"),
    [Input({"type": "interval-traffic-status", "id": MATCH}, "n_intervals")],
)
def update_traffic_status(n):
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
                    html.Div(
                        className="col-md-3",
                        children=[
                            html.Label(
                                f"Status: {get_traffic_conclusion(processor.video.detections_manager.counter_time[zone]['real_waiting_time'])}"
                            ),
                        ],
                    ),
                ],
            )
        )
    return children
