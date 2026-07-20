"""
Run the fine-tuned YOLOv8m model on a sample image.

Usage:
    uv run python sample.py
    uv run python sample.py --source samples/example.jpg --conf 0.3
    uv run python sample.py --source path/to/image.jpg --show
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ultralytics import YOLO


def main() -> None:
    parser = argparse.ArgumentParser(description="Run YOLOv8m vehicle detection on an image")
    parser.add_argument(
        "--weights",
        type=str,
        default="weights/train34.pt",
        help="Path to model weights",
    )
    parser.add_argument(
        "--source",
        type=str,
        default="samples/example.jpg",
        help="Path to input image",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.3,
        help="Confidence threshold",
    )
    parser.add_argument(
        "--iou",
        type=float,
        default=0.7,
        help="NMS IoU threshold",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="samples/example_pred.jpg",
        help="Where to save the annotated image",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Open a window with the result (needs a display)",
    )
    args = parser.parse_args()

    source = Path(args.source)
    if not source.is_file():
        raise SystemExit(f"Image not found: {source}")

    print(f"Loading model: {args.weights}")
    model = YOLO(args.weights)

    print(f"Running inference on: {source}")
    results = model.predict(
        source=str(source),
        conf=args.conf,
        iou=args.iou,
        verbose=False,
    )
    result = results[0]

    names = result.names
    boxes = result.boxes
    if boxes is None or len(boxes) == 0:
        print("No detections.")
    else:
        print(f"Detections: {len(boxes)}")
        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            xyxy = box.xyxy[0].tolist()
            label = names.get(cls_id, str(cls_id))
            print(f"  - {label:8s} conf={conf:.2f}  box={[round(v, 1) for v in xyxy]}")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    result.save(filename=str(out))
    print(f"Saved annotated image -> {out}")

    if args.show:
        result.show()


if __name__ == "__main__":
    main()
