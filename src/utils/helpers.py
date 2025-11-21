# src/utils/helpers.py
import os
from pathlib import Path
from datetime import datetime

def ensure_dir(p):
    Path(p).mkdir(parents=True, exist_ok=True)

def timestamp(fmt="%Y%m%d_%H%M%S"):
    return datetime.now().strftime(fmt)

def save_image(frame, outdir, prefix="img"):
    ensure_dir(outdir)
    fname = f"{prefix}_{timestamp()}.jpg"
    path = Path(outdir) / fname
    import cv2
    cv2.imwrite(str(path), frame)
    return str(path)
