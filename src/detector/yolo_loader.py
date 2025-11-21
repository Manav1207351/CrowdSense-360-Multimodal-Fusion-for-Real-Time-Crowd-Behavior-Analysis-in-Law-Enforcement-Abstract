# src/detectors/yolo_loader.py
from ultralytics import YOLO
from pathlib import Path

def load_yolo(path, device="cpu"):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"YOLO model not found: {p}")
    model = YOLO(str(p))
    # set device if needed (ultralytics chooses automatically)
    model.to(device)
    return model
