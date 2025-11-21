from ultralytics import YOLO

model = YOLO("D:/CrowedSense 360/src/detectors/runs/classify/train16/weights/last.pt")
metrics = model.val()   # evaluates on val set
print(metrics)
