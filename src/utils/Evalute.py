from ultralytics import YOLO

# Crowd
crowd = YOLO("models/crowd_yolo6/weights/best.pt")
crowd.val()

# Weapon
weapon = YOLO("models/weapon_yolo/weights/best.pt")
weapon.val()

# Fight
fight = YOLO("models/fight_yolo/weights/best.pt")
fight.val()
