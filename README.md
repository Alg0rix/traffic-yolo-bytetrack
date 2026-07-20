# Traffic YOLO + ByteTrack

Minimal realtime traffic flow analysis using **YOLOv8m** (fine-tuned vehicle detector) and **ByteTrack**, with a small Dash web UI.

## What’s included

| Path | Description |
|------|-------------|
| `weights/train34.pt` | Fine-tuned YOLOv8m weights (~50 MB) |
| `samples/intersection.mp4` | Sample intersection video |
| `app.py` | Dash + Flask app entrypoint |
| `vision.py` | Detection, tracking, zone logic |
| `zones.yaml` | Entry/exit polygon zones |
| `pyproject.toml` | Dependencies managed with **uv** |

## Requirements

- Python **3.10** or **3.11**
- [uv](https://docs.astral.sh/uv/)
- NVIDIA GPU optional (CUDA speeds up inference; CPU works but is slower)

## Setup (uv)

```bash
# Install uv if needed: https://docs.astral.sh/uv/getting-started/installation/
git clone https://github.com/Alg0rix/traffic-yolo-bytetrack.git
cd traffic-yolo-bytetrack

# Create venv + install deps from pyproject.toml
uv sync
```

## Run

Default weights + sample video:

```bash
uv run python app.py
```

Then open **http://localhost:5000** (video stream also at `/video_feed`).

### Custom video / weights

```bash
uv run python app.py \
  --source-weights-path weights/train34.pt \
  --source-video-path samples/intersection.mp4 \
  --confidence-threshold 0.3 \
  --iou-threshold 0.7 \
  --config zones.yaml \
  --port 5000
```

### CLI options

| Flag | Default | Description |
|------|---------|-------------|
| `--source-weights-path` | `weights/train34.pt` | Model checkpoint |
| `--source-video-path` | `samples/intersection.mp4` | Input video or path |
| `--confidence-threshold` | `0.3` | Detection confidence |
| `--iou-threshold` | `0.7` | NMS IoU |
| `--config` | `zones.yaml` | Zone polygons |
| `--host` | `0.0.0.0` | Bind address |
| `--port` | `5000` | HTTP port |

## Model

- **Architecture:** Ultralytics YOLOv8 **medium** (`yolov8m`)
- **Weights:** `weights/train34.pt` (fine-tuned vehicle detector)
- **Tracker:** ByteTrack (`supervision`)
- **Training dataset:** [Vehicle (Roboflow Universe)](https://universe.roboflow.com/marchel-maulana-fahrezi/vehicle-emspn) by marchel-maulana-fahrezi

## Project layout

```
.
├── app.py              # Web UI + video feed
├── vision.py           # YOLO + ByteTrack pipeline
├── detections.py       # Zone / path bookkeeping
├── processor.py        # Processor singleton
├── configurator.py     # zones.yaml loader
├── coordinate.py       # Polygon helpers for the UI
├── zones.yaml          # Entry / exit zones
├── weights/train34.pt
├── samples/intersection.mp4
├── components/         # Dash UI pieces
├── pages/
├── pyproject.toml
└── README.md
```

## Dataset

Training images and labels come from Roboflow Universe:

**https://universe.roboflow.com/marchel-maulana-fahrezi/vehicle-emspn**

Export as YOLOv8 format if you want to retrain. Full image sets are not shipped in this repo (weights only).

## Notes

- Zone coordinates in `zones.yaml` are tuned for the sample / original camera geometry. For a new camera, redraw zones in the UI or edit the config.
- Large training datasets and experiment logs are intentionally **not** included.

## License

School / research project code — use at your own discretion.
