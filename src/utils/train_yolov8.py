# src/detectors/infer_detector.py
# Real-time inference script: detection + simple track + OCR for plates + rule-based events (weapons + violence)

import argparse
import os
import time
import pathlib
import sys
import cv2
import numpy as np
from ultralytics import YOLO
import easyocr

# -------------------------------
# Import tracker
# -------------------------------
repo_root = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))

from src.trackers.bytetrack_wrapper import SimpleTracker

# -------------------------------
# Classes (make sure your model matches these)
# -------------------------------
CLASS_NAMES = ['person', 'bag', 'weapon', 'bike', 'license_plate']


def draw_box(im, box, label, color=(0, 255, 0)):
    x1, y1, x2, y2 = map(int, box)
    cv2.rectangle(im, (x1, y1), (x2, y2), color, 2)
    cv2.putText(im, label, (x1, max(15, y1 - 5)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)


def main(args):
    # -------------------------------
    # Load model, OCR, tracker
    # -------------------------------
    model = YOLO(args.weights)
    reader = easyocr.Reader(['en'], gpu=False) if args.ocr else None
    tracker = SimpleTracker(max_age=30)

    cap = cv2.VideoCapture(int(args.video) if args.video.isdigit() else args.video)
    if not cap.isOpened():
        print(f"❌ Cannot open video source: {args.video}")
        return

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0

    os.makedirs("outputs", exist_ok=True)
    out_writer = None
    if args.save_out:
        out_writer = cv2.VideoWriter(
            "outputs/out.mp4",
            cv2.VideoWriter_fourcc(*'mp4v'),
            fps,
            (w, h)
        )

    frame_id = 0
    weapon_detected = {}
    last_alert = {}

    prev_gray = None  # for motion-based violence detection

    # -------------------------------
    # Main loop
    # -------------------------------
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_id += 1

        # Run YOLOv8 inference
        res = model.predict(frame, imgsz=args.imgsz, verbose=False)[0]

        # Collect detections
        dets = []
        if hasattr(res, "boxes") and len(res.boxes):
            for b in res.boxes:
                conf = float(b.conf.cpu().numpy())
                cls = int(b.cls.cpu().numpy())
                if conf < args.conf_thresh:
                    continue
                bbox = b.xyxy.cpu().numpy().reshape(-1).tolist()
                dets.append({'bbox': bbox, 'cls': cls, 'conf': conf})

        # Update tracker
        tracks = tracker.update(dets)

        persons = []  # collect person detections
        for tid, t in tracks.items():
            bbox = t['bbox']
            cls_id = t['cls']
            cls_name = CLASS_NAMES[cls_id] if cls_id < len(CLASS_NAMES) else f"class{cls_id}"
            label = f"ID{tid}:{cls_name}"
            draw_box(frame, bbox, label)

            # --- Weapon rule ---
            if cls_name == 'weapon':
                weapon_detected[tid] = weapon_detected.get(tid, 0) + 1
                if weapon_detected[tid] >= 2:
                    now = time.time()
                    if last_alert.get(('weapon', tid), 0) + args.alert_cooldown < now:
                        last_alert[('weapon', tid)] = now
                        os.makedirs("alerts", exist_ok=True)
                        x1, y1, x2, y2 = map(int, bbox)
                        cv2.imwrite(f"alerts/weapon_tid{tid}_{int(now)}.jpg",
                                    frame[y1:y2, x1:x2])
                        print(f"[ALERT] Weapon detected on track {tid}")
            else:
                weapon_detected[tid] = max(0, weapon_detected.get(tid, 0) - 1)

            # --- License plate OCR ---
            if cls_name in ('license_plate', 'plate') and reader is not None:
                x1, y1, x2, y2 = map(int, bbox)
                crop = frame[y1:y2, x1:x2]
                if crop.size:
                    try:
                        ocr = reader.readtext(crop, detail=0)
                        if ocr:
                            text = ocr[0]
                            cv2.putText(frame, f"PL:{text}",
                                        (x1, y2 + 20),
                                        cv2.FONT_HERSHEY_SIMPLEX,
                                        0.7, (255, 255, 0), 2)
                    except Exception as e:
                        print("OCR error:", e)

            if cls_name == "person":
                persons.append(t)

        # -------------------------------
        # Violence Rule (motion + multiple persons)
        # -------------------------------
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev_gray is not None and len(persons) >= 2:
            flow = cv2.calcOpticalFlowFarneback(prev_gray, gray,
                                                None, 0.5, 3, 15, 3, 5, 1.2, 0)
            mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            motion_level = np.mean(mag)

            if motion_level > 3.5:  # threshold for strong motion
                now = time.time()
                if last_alert.get('violence', 0) + args.alert_cooldown < now:
                    last_alert['violence'] = now
                    os.makedirs("alerts", exist_ok=True)
                    cv2.imwrite(f"alerts/violence_{int(now)}.jpg", frame)
                    print("[ALERT] Violence detected (motion + crowd)!")
                cv2.putText(frame, "⚠️ VIOLENCE DETECTED", (50, 120),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

        prev_gray = gray

        # -------------------------------
        # Display + save
        # -------------------------------
        cv2.imshow("CrowdSense360", frame)
        if out_writer:
            out_writer.write(frame)

        if cv2.waitKey(1) & 0xFF == 27:  # Esc to quit
            break

    cap.release()
    if out_writer:
        out_writer.release()
    cv2.destroyAllWindows()
    print("✅ Inference finished.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=str, default="0",
                        help="Video path or webcam index (use 0 for webcam)")
    parser.add_argument("--weights", type=str, default="yolov8n.pt",
                        help="YOLO model weights path")
    parser.add_argument("--imgsz", type=int, default=1280,
                        help="Inference image size")
    parser.add_argument("--conf_thresh", type=float, default=0.35,
                        help="Confidence threshold")
    parser.add_argument("--ocr", action="store_true",
                        help="Enable EasyOCR for license plates")
    parser.add_argument("--save_out", action="store_true",
                        help="Save output video to outputs/out.mp4")
    parser.add_argument("--alert_cooldown", type=float, default=6.0,
                        help="Seconds between repeated alerts")
    args = parser.parse_args()

    main(args)
