import argparse

import cv2
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, no_update
from flask import Flask, Response

from configurator import config_loader
from pages import home
from processor import video_processor_manager as processor
from components import Navbar
from vision import COUNTER_ZONE

server = Flask(__name__)
app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)


def gen():
    for frame in processor.video.process_video():
        _, jpeg = cv2.imencode(".jpg", frame)
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n\r\n"
        )


@server.route("/video_feed")
def video_feed():
    return Response(gen(), mimetype="multipart/x-mixed-replace; boundary=frame")


app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        Navbar.navbar(),
        html.Div(id="page-content", children=home.layout),
    ]
)


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname in ("/", "/camera", "/traffic"):
        return home.layout
    return no_update


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Traffic Flow Analysis using YOLOv8m and ByteTrack"
    )
    parser.add_argument(
        "--source-weights-path",
        type=str,
        default="weights/train34.pt",
        help="Path to model weights (default: weights/train34.pt)",
    )
    parser.add_argument(
        "--source-video-path",
        type=str,
        default="samples/intersection.mp4",
        help="Path to source video (default: samples/intersection.mp4)",
    )
    parser.add_argument(
        "--target-video-path",
        type=str,
        default=None,
        help="Optional path to save annotated video",
    )
    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.3,
        help="Detection confidence threshold",
    )
    parser.add_argument(
        "--iou-threshold",
        type=float,
        default=0.7,
        help="NMS IoU threshold",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="zones.yaml",
        help="Zones config file",
    )
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()

    zone_in, zone_out = config_loader(args.config)
    processor.init(
        source_weights_path=args.source_weights_path,
        source_video_path=args.source_video_path,
        target_video_path=args.target_video_path,
        confidence_threshold=args.confidence_threshold,
        iou_threshold=args.iou_threshold,
        zone_in_polygons=zone_in,
        zone_out_polygons=zone_out,
        counter_zone_polygons=COUNTER_ZONE,
        config=(zone_in, zone_out),
    )
    app.run(host=args.host, port=args.port, debug=False)
