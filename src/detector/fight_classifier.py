# src/detector/fight_classifier.py

import cv2
import torch
from ultralytics import YOLO
import time

class FightClassifier:
    def __init__(self, model_path, device="auto", img_size=480, skip_frames=2):
        try:
            print(f"\nLoading Fight Model: {model_path}")

            if device == "auto":
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            else:
                self.device = device

            print("Using device:", self.device)

            self.model = YOLO(model_path)
            self.model.to(self.device)

            # ---- Detect fight class index automatically ----
            self.fight_class_id = None
            for cid, name in self.model.names.items():
                if name.lower() in ["fight", "violence", "fighting"]:
                    self.fight_class_id = cid
                    break

            print("Model classes:", self.model.names)
            print("Fight class index =", self.fight_class_id)

            self.img_size = img_size
            self.skip_frames = skip_frames
            self.counter = 0

            # Warm up
            dummy = (255 * torch.rand(480, 480, 3).numpy()).astype("uint8")
            dummy = cv2.resize(dummy, (img_size, img_size))
            for _ in range(3):
                self.model(dummy, verbose=False)
            print("Fight model warm-up done.\n")

        except Exception as e:
            raise RuntimeError(f"Failed to load fight model: {e}")

    def predict(self, frame):
        self.counter += 1
        if self.counter % self.skip_frames != 0:
            return 0.0
        
        try:
            resized = cv2.resize(frame, (self.img_size, self.img_size))
            results = self.model(resized, verbose=False, device=self.device)[0]

            fight_score = 0.0

            for box in results.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])

                # --- Correct fight class ---
                if cls_id == self.fight_class_id:
                    fight_score = max(fight_score, conf)

            return fight_score

        except Exception as e:
            print("Fight detection error:", e)
            return 0.0

    def predict_from_frame(self, frame):
        return self.predict(frame)
