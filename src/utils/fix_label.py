from ultralytics import YOLO
import os
import shutil

# ------------------------------
# 1. Load pretrained YOLO model (safe)
# ------------------------------
model = YOLO("yolov8m.pt")  # yolov8s.pt or yolov8m.pt

# ------------------------------
# 2. Dataset paths
# ------------------------------
DATASET_PATH = r"D:/CrowedSense 360/datasets/Weapons"

TRAIN_IMAGES = os.path.join(DATASET_PATH, "D:/CrowedSense 360/datasets/Weapons/images/train")
VAL_IMAGES   = os.path.join(DATASET_PATH, "D:/CrowedSense 360/datasets/Weapons/images/val")

TRAIN_LABELS = os.path.join(DATASET_PATH, "labels/train")
VAL_LABELS   = os.path.join(DATASET_PATH, "labels/val")

# Create labels folders if they don't exist
os.makedirs(TRAIN_LABELS, exist_ok=True)
os.makedirs(VAL_LABELS, exist_ok=True)

# ------------------------------
# 3. Auto-label function (memory-friendly)
# ------------------------------
def auto_label(input_folder, output_label_folder):
    print(f"\n🔵 Auto-labeling: {input_folder}")

    # Run YOLO prediction on images in the folder
    results = model.predict(
        source=input_folder,
        save_txt=True,       # Save YOLO-format labels
        save_conf=False,     # Only bounding boxes, no confidence
        conf=0.25,           # Confidence threshold
        imgsz=640,           # Resize large images to 640x640
        batch=1              # Process 1 image at a time to save memory
    )

    # YOLO saves labels temporarily in runs/detect/predict*/labels
    latest_run = model.predictor.save_dir
    labels_dir = os.path.join(latest_run, "labels")

    # Copy generated labels to your dataset labels folder
    for file in os.listdir(labels_dir):
        src = os.path.join(labels_dir, file)
        dst = os.path.join(output_label_folder, file)
        shutil.copy(src, dst)

    print(f"✅ Labels created for: {input_folder}")

# ------------------------------
# 4. Auto-label both train & val
# ------------------------------
auto_label(TRAIN_IMAGES, TRAIN_LABELS)
auto_label(VAL_IMAGES, VAL_LABELS)

print("\n🎉 All YOLO labels for train and val images are generated successfully!")
