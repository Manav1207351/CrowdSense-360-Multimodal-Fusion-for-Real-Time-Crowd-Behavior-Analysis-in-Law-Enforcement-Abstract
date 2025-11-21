import os
import shutil
import random
from pathlib import Path

# Source (where extracted frames are stored)
SOURCE_DIR = Path("D:/CrowedSense 360/video_frames")  # weapons/, fight/, normal/, violence/, plate/

# Destination (YOLOv8 dataset format)
DEST_DIR = Path("D:/CrowedSense 360/datasets/yolo_classify_dataset")
TRAIN_DIR = DEST_DIR / "train"
VAL_DIR = DEST_DIR / "val"

# Train/Val split ratio
SPLIT_RATIO = 0.8  # 80% train, 20% val

# Ensure dirs exist
for d in [TRAIN_DIR, VAL_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Process each class
for class_name in os.listdir(SOURCE_DIR):
    class_dir = SOURCE_DIR / class_name
    if not class_dir.is_dir():
        continue

    images = list(class_dir.glob("*.jpg"))
    random.shuffle(images)

    split_idx = int(len(images) * SPLIT_RATIO)
    train_imgs = images[:split_idx]
    val_imgs = images[split_idx:]

    # Create class subfolders
    (TRAIN_DIR / class_name).mkdir(parents=True, exist_ok=True)
    (VAL_DIR / class_name).mkdir(parents=True, exist_ok=True)

    # Copy files
    for img in train_imgs:
        shutil.copy(img, TRAIN_DIR / class_name / img.name)
    for img in val_imgs:
        shutil.copy(img, VAL_DIR / class_name / img.name)

    print(f"[INFO] {class_name}: {len(train_imgs)} train, {len(val_imgs)} val")

print("✅ Dataset prepared at:", DEST_DIR)
