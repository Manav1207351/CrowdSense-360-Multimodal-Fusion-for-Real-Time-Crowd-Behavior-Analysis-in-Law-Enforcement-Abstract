from ultralytics import YOLO

# --------------------------
# Train 1: CROWD DETECTOR
# --------------------------
#print("🚀 Training Crowd Detection Model...")
#crowd_model = YOLO("yolov8n.pt")  # base model
#crowd_model.train(
 #   data="datasets/crowd/data.yaml",
  #epochs=5,
   # imgsz=224,
    #batch=16,
  #  name="crowd_yolo",
   # project="models"
#)

# --------------------------
# Train 2: WEAPON DETECTOR
# --------------------------
print("🔫 Training Weapon Detection Model...")
weapon_model = YOLO("yolov8l.pt")
weapon_model.train(
    data="D:\CrowedSense 360\datasets\Weapons\datas.yaml",  # ✅ must point to that file
    epochs=10,
    imgsz=640,
    batch=16,
    project="models",           
    name="weapon_yolo"
)


# --------------------------
# Train 3: FIGHT CLASSIFIER
# --------------------------
#print("🥊 Training Fight Recognition Model...")
#fight_model = YOLO("yolov8n.pt") # classification variant
#fight_model.train(
 #   data="datasets/Figth/data.yaml",
  #  epochs=10,
  #  imgsz=640,
   # batch=16, 
   # name="fight_yolo",
    #project="models"
#)   
 