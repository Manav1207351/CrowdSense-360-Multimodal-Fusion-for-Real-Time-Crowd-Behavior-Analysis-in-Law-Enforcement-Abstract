from ultralytics import YOLO

# --------------------------
# Train 1: CROWD DETECTOR
# --------------------------
print("🚀 Training Crowd Detection Model...")
crowd_model = YOLO("yolov8n.pt")  # base model
crowd_model.train(
    data="datasets/crowd/data.yaml",
    epochs=50,
    imgsz=640,
    batch=16,
    name="crowd_yolo",
    project="models"
)

# --------------------------
# Train 2: WEAPON DETECTOR
# --------------------------
print("🔫 Training Weapon Detection Model...")
weapon_model = YOLO("yolov8n.pt")
weapon_model.train(
    data="datasets/weapons/data.yaml",
    epochs=60,
    imgsz=640,
    batch=16,
    name="weapon_yolo",
    project="models"
)

# --------------------------
# Train 3: FIGHT CLASSIFIER
# --------------------------
print("🥊 Training Fight Recognition Model...")
fight_model = YOLO("yolov8n-cls.pt")  # classification variant
fight_model.train(
    data="datasets/fight",
    epochs=40,
    imgsz=224,
    batch=16,
    name="fight_yolo",
    project="models"
)
