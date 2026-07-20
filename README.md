# Traffic YOLO + ByteTrack

Minimal realtime traffic flow analysis using **YOLOv8m** (fine-tuned vehicle detector) and **ByteTrack**, with a small Dash web UI.

This repository supports the research published in *Jurnal Teknik Informatika (JUTIF)*.

## Publication

**Traffic Flow and Congestion Detection with YOLOv8 and ByteTrack-Based Multi Object Tracking**

| | |
|---|---|
| **Authors** | Marchel Maulana Fahrezi, Eka Angga Laksana |
| **Affiliation** | Faculty of Engineering, Universitas Widyatama, Indonesia |
| **Journal** | [Jurnal Teknik Informatika (JUTIF)](https://jutif.if.unsoed.ac.id/) |
| **Issue** | Vol. 5 No. 4 (August 2024), pp. 253–261 |
| **DOI** | [10.52436/1.jutif.2024.5.4.2063](https://doi.org/10.52436/1.jutif.2024.5.4.2063) |
| **Article** | [jutif.if.unsoed.ac.id/…/2063](https://jutif.if.unsoed.ac.id/index.php/jurnal/article/view/2063) |
| **Keywords** | ByteTrack, Congestion Estimation, Traffic Counter, Vehicle Detection, YOLOv8 |

### Abstract

The rapid urbanization witnessed in cities like Bandung, Indonesia, has emerged as a pressing issue, precipitating severe traffic congestion that poses challenges to economic growth and diminishes overall quality of life. This study develops a real-time traffic surveillance and control system that uses the city’s existing CCTV infrastructure with **YOLOv8** for vehicle detection and **ByteTrack** for real-time multi-object tracking. Evaluated at several locations in Bandung, YOLOv8 achieved about **80%** vehicle detection accuracy, ByteTrack about **17%** average error in vehicle counting, and the combined multi-object tracking approach about **80%** accuracy in congestion detection.

### Cite

```
M. M. Fahrezi and E. A. Laksana, “Traffic Flow and Congestion Detection with
YOLOv8 and ByteTrack-Based Multi Object Tracking,” J. Tek. Inform. (JUTIF),
vol. 5, no. 4, pp. 253–261, Aug. 2024, doi: 10.52436/1.jutif.2024.5.4.2063.
```

## What’s included

| Path | Description |
|------|-------------|
| `weights/train34.pt` | Fine-tuned YOLOv8m weights (~50 MB) |
| `samples/example.jpg` | Example frame for quick inference |
| `samples/intersection.mp4` | Sample intersection video |
| `sample.py` | Run model on an image (CLI) |
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

### Sample inference on an image

Quick check that the model works (uses `samples/example.jpg`):

```bash
uv run python sample.py
```

This prints detections and writes `samples/example_pred.jpg`.

```bash
# custom image / thresholds
uv run python sample.py --source samples/example.jpg --conf 0.3 --output samples/example_pred.jpg

# open a preview window (needs a display)
uv run python sample.py --show
```

### Web app (video + UI)

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
├── sample.py           # Image inference demo
├── vision.py           # YOLO + ByteTrack pipeline
├── detections.py       # Zone / path bookkeeping
├── processor.py        # Processor singleton
├── configurator.py     # zones.yaml loader
├── coordinate.py       # Polygon helpers for the UI
├── zones.yaml          # Entry / exit zones
├── weights/train34.pt
├── samples/
│   ├── example.jpg
│   └── intersection.mp4
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

Research / academic project code associated with the JUTIF 2024 publication above — use at your own discretion.
