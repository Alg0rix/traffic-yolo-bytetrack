from dash import Input, Output, no_update, State, Patch, MATCH, ALL, callback
from dash.dependencies import Input, Output
from dash import html, dcc, callback
import dash
from processor import video_processor_manager as processor
import plotly.express as px
import json
from coordinate import coordinate_extractor
import yaml

ZONES = []

config_px = {
    "modeBarButtonsToAdd": [
        "drawclosedpath",
        "eraseshape",
    ]
}


def add_counter_zone_form():
    zone_id = "counter-zone"
    input_zone_input = dcc.Input(
        id="input-counter-zone",
        placeholder="Input Zone",
        type="text",
        className="form-control mb-2",
    )

    output_zone_input = dcc.Input(
        id="output-counter-zone",
        placeholder="Output Zone",
        type="text",
        className="form-control mb-2",
    )

    save_button = html.Button(
        "Save",
        id="save-counter-zone",
        className="btn btn-primary",
        style={"margin-right": "5px"},
    )

    delete_button = html.Button(
        "Delete",
        id="delete-counter-zone",
        className="btn btn-danger",
        style={"margin-right": "5px"},
    )

    bgr_frame = processor.video.current_frame[:, :, ::-1]

    current_frame_fig = px.imshow(bgr_frame)

    current_frame_fig.update_layout(
        dragmode="drawclosedpath",
    )

    counter_zone_annotator_layout = html.Div(
        children=[
            dcc.Graph(
                id="counter-zone-annotator",
                figure=current_frame_fig,
                config=config_px,
            ),
            html.Pre(id="counter-zone-annotator-data"),
        ],
    )

    counter_zone_form = html.Div(
        id=zone_id,
        className="card mb-2",
        children=[
            html.Div(
                className="card-body",
                children=[
                    html.H5("Counter Zone", className="card-title"),
                    html.Div(
                        className="row",
                        children=[
                            html.Div(
                                className="col-md-3",
                                children=[
                                    html.Label("Input Zone"),
                                    input_zone_input,
                                ],
                            ),
                            html.Div(
                                className="col-md-3",
                                children=[
                                    html.Label("Output Zone"),
                                    output_zone_input,
                                ],
                            ),
                            html.Div(
                                className="col-md-3",
                                children=[
                                    save_button,
                                    delete_button,
                                ],
                            ),
                            # status of save
                            html.Div(
                                id="save-status",
                                className="col-md-3",
                                children=[
                                    "Not Saved",
                                ],
                            ),
                        ],
                    ),
                    counter_zone_annotator_layout,
                ],
            ),
        ],
    )

    return counter_zone_form


def add_entry_zone_form(id, zone_name=None, input_zone=None, output_zone=None):
    zone_id = f"zone-{id}"
    zone_name_input = dcc.Input(
        id={"type": "zone-name", "index": zone_id},
        placeholder="Zone Name",
        type="text",
        className="form-control mb-2",
        value=zone_name,
    )
    input_zone_input = dcc.Input(
        id={"type": "input-zone", "index": zone_id},
        placeholder="Input Zone",
        type="text",
        className="form-control mb-2",
        value=input_zone,
    )
    output_zone_input = dcc.Input(
        id={"type": "output-zone", "index": zone_id},
        placeholder="Output Zone",
        type="text",
        className="form-control mb-2",
        value=output_zone,
    )
    save_button = html.Button(
        "Save",
        id={"type": "save", "index": zone_id},
        className="btn btn-primary",
        style={"margin-right": "5px"},
    )
    delete_button = html.Button(
        "Delete",
        id={"type": "delete-zone", "index": zone_id},
        className="btn btn-danger",
        style={"margin-right": "5px"},
    )
    bgr_frame = processor.video.current_frame[:, :, ::-1]
    current_frame_fig = px.imshow(bgr_frame)
    current_frame_fig.update_layout(
        dragmode="drawclosedpath",
    )
    # if input_zone is not None and output_zone is not None:
    #     input_zone = str(input_zone)
    #     output_zone = str(output_zone)
    #     current_frame_fig.add_shape(
    #         type="path",
    #         path=input_zone,
    #         line=dict(
    #             color="RoyalBlue",
    #         ),
    #     )
    #     current_frame_fig.add_shape(
    #         type="path",
    #         path=output_zone,
    #         line=dict(
    #             color="Crimson",
    #         ),
    #     )
    zone_annotator_layout = html.Div(
        children=[
            dcc.Graph(
                id={"type": "zone-annotator", "index": zone_id},
                figure=current_frame_fig,
                config=config_px,
            ),
            html.Pre(id={"type": "zone-annotator-data", "index": zone_id}),
        ],
    )

    zone_form = html.Div(
        id=zone_id,
        className="card mb-2",
        children=[
            html.Div(
                className="card-body",
                children=[
                    html.H5(f"Entry Zone {id}", className="card-title"),
                    html.Div(
                        className="row",
                        children=[
                            html.Div(
                                className="col-md-3",
                                children=[
                                    html.Label("Zone Name"),
                                    zone_name_input,
                                ],
                            ),
                            html.Div(
                                className="col-md-3",
                                children=[
                                    html.Label("Input Zone"),
                                    input_zone_input,
                                ],
                            ),
                            html.Div(
                                className="col-md-3",
                                children=[
                                    html.Label("Output Zone"),
                                    output_zone_input,
                                ],
                            ),
                            html.Div(
                                className="col-md-3",
                                children=[
                                    save_button,
                                    delete_button,
                                ],
                            ),
                            # status of save
                            html.Div(
                                id={"type": "save-status", "index": zone_id},
                                className="col-md-3",
                                children=[
                                    "Not Saved",
                                ],
                            ),
                        ],
                    ),
                    zone_annotator_layout,
                ],
            ),
        ],
    )

    return zone_form


# @callback(
#     Output("zone-form", "children", allow_duplicate=True),
#     Input("load-zone-button", "n_clicks"),
#     prevent_initial_call=True,
# )
# def load_zones(n_clicks):
#     patched_list = Patch()
#     for id, zone in enumerate(zip(processor.config[0], processor.config[1])):
#         zone_in, zone_out = zone
#         patched_list.append(add_entry_zone_form(id))

#     return patched_list

#     return no_update


@callback(
    Output("zone-form", "children", allow_duplicate=True),
    [
        Input("add-zone-button", "n_clicks"),
        Input("load-zone-button", "n_clicks"),
        Input({"type": "delete-zone", "index": ALL}, "n_clicks"),
    ],
    [
        State("zone-form", "children"),
        State({"type": "zone-name", "index": ALL}, "value"),
        State({"type": "input-zone", "index": ALL}, "value"),
        State({"type": "output-zone", "index": ALL}, "value"),
        State("zone-type-dropdown", "value"),
    ],
    prevent_initial_call=True,
)
def manage_zones(
    n_clicks_add,
    n_clicks_load,
    n_clicks_delete,
    current_children,
    zone_names,
    input_zones,
    output_zones,
    zone_type,
):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None

    patched_list = Patch()

    if triggered_id == "add-zone-button":
        if n_clicks_add is None:
            return current_children
        if zone_type == "counter_zone":
            # check if counter zone already exist
            for child in current_children:
                if child["props"]["id"] == "counter-zone":
                    return current_children
            patched_list.append(add_counter_zone_form())
        elif zone_type == "entry_zone":
            patched_list.append(add_entry_zone_form(n_clicks_add))
    elif triggered_id == "load-zone-button":
        if n_clicks_load is None:
            return current_children
        for id, zone in enumerate(zip(processor.config[0], processor.config[1])):
            input_zone, output_zone = zone
            patched_list.append(add_entry_zone_form(id, id, input_zone, output_zone))
    else:
        zone_id = json.loads(triggered_id)["index"]
        patched_list = [
            child for child in current_children if child["props"]["id"] != zone_id
        ]

    return patched_list


@callback(
    [
        Output({"type": "input-zone", "index": MATCH}, "value"),
        Output({"type": "output-zone", "index": MATCH}, "value"),
    ],
    Input({"type": "zone-annotator", "index": MATCH}, "relayoutData"),
    prevent_initial_call=True,
)
def update_zone_annotator(relayoutData):
    if "shapes" in relayoutData:
        shapes = relayoutData["shapes"]
        if len(shapes) == 2:
            return (
                shapes[0]["path"],
                shapes[1]["path"],
            )
    return no_update, no_update


@callback(
    Output({"type": "save-status", "index": MATCH}, "children"),
    Input({"type": "save", "index": MATCH}, "n_clicks"),
    [
        State({"type": "zone-name", "index": MATCH}, "value"),
        State({"type": "input-zone", "index": MATCH}, "value"),
        State({"type": "output-zone", "index": MATCH}, "value"),
    ],
    prevent_initial_call=True,
)
def toggle_save(n_clicks, zone_name, input_zone, output_zone):
    ZONES.append(
        {
            "zone_name": zone_name,
            "input_zone": coordinate_extractor(input_zone),
            "output_zone": coordinate_extractor(output_zone),
        }
    )
    yaml.dump(ZONES, open("zones.yaml", "w"))
    return "saved at {}".format(n_clicks)
