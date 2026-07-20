"""
Fine-tune YOLOv8 on a vehicle dataset (Ultralytics).

Examples:
    # Quick smoke train on the bundled tiny example (CPU/GPU)
    uv run python finetune.py

    # Full-ish fine-tune from COCO-pretrained YOLOv8m
    uv run python finetune.py \\
      --model yolov8m.pt \\
      --data /path/to/your/data.yaml \\
      --epochs 100 --imgsz 640 --batch 8

    # Continue from this repo's checkpoint
    uv run python finetune.py \\
      --model weights/train34.pt \\
      --data datasets/example/data.yaml \\
      --epochs 30 --name vehicles_ft

After training, best weights are under:
    runs/detect/<name>/weights/best.pt

Then run inference:
    uv run python sample.py --weights runs/detect/<name>/weights/best.pt
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ultralytics import YOLO


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Fine-tune YOLOv8 for vehicle detection (Bike / Car by default)"
    )
    p.add_argument(
        "--model",
        type=str,
        default="yolov8m.pt",
        help="Base weights or YAML (default: yolov8m.pt — downloaded if missing)",
    )
    p.add_argument(
        "--data",
        type=str,
        default="datasets/example/data.yaml",
        help="Path to data.yaml (default: datasets/example/data.yaml)",
    )
    p.add_argument("--epochs", type=int, default=5, help="Training epochs")
    p.add_argument("--imgsz", type=int, default=640, help="Train image size")
    p.add_argument("--batch", type=int, default=4, help="Batch size")
    p.add_argument(
        "--device",
        type=str,
        default=None,
        help="Device: 0, 0,1, cpu, mps (default: auto)",
    )
    p.add_argument(
        "--project",
        type=str,
        default="runs/detect",
        help="Project directory for runs",
    )
    p.add_argument(
        "--name",
        type=str,
        default="finetune",
        help="Run name (output under project/name)",
    )
    p.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Dataloader workers",
    )
    p.add_argument(
        "--patience",
        type=int,
        default=50,
        help="Early-stopping patience (epochs)",
    )
    p.add_argument(
        "--resume",
        action="store_true",
        help="Resume last training run if interrupted",
    )
    p.add_argument(
        "--exist-ok",
        action="store_true",
        help="Overwrite existing run directory with the same name",
    )
    return p.parse_args()


def resolve_data_yaml(data_arg: str) -> Path:
    """Return absolute data.yaml, rewriting relative `path:` to the yaml directory."""
    data_path = Path(data_arg).expanduser().resolve()
    if not data_path.is_file():
        raise SystemExit(
            f"data.yaml not found: {data_path}\n"
            "Download a YOLOv8 dataset (e.g. from Roboflow) or use datasets/example/data.yaml"
        )

    # Ultralytics may resolve relative paths against its global datasets_dir.
    # Rewrite a local data.yaml so `path` is absolute next to the file.
    text = data_path.read_text(encoding="utf-8")
    root = data_path.parent.resolve()
    lines = []
    replaced = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("path:"):
            # path: .  or path: something relative
            lines.append(f"path: {root.as_posix()}")
            replaced = True
        else:
            lines.append(line)
    if not replaced:
        lines.insert(0, f"path: {root.as_posix()}")

    fixed = data_path.with_name("data.local.yaml")
    fixed.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return fixed


def main() -> None:
    args = parse_args()
    data_path = resolve_data_yaml(args.data)

    print(f"Base model : {args.model}")
    print(f"Dataset    : {data_path}")
    print(f"Epochs     : {args.epochs}  imgsz={args.imgsz}  batch={args.batch}")

    model = YOLO(args.model)
    results = model.train(
        data=str(data_path),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        project=args.project,
        name=args.name,
        workers=args.workers,
        patience=args.patience,
        resume=args.resume,
        exist_ok=args.exist_ok,
        pretrained=True,
        plots=True,
    )

    run_dir = Path(results.save_dir)
    best = run_dir / "weights" / "best.pt"
    last = run_dir / "weights" / "last.pt"
    print("\nTraining finished.")
    print(f"  run dir : {run_dir}")
    if best.is_file():
        print(f"  best    : {best}")
        print(f"\nTry inference:")
        print(f"  uv run python sample.py --weights {best} --source samples/frame_775.jpg")
    if last.is_file():
        print(f"  last    : {last}")


if __name__ == "__main__":
    main()
