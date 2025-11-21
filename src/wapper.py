import cv2
import time
from .infer_detector import detect_crowd, detect_fight, detect_weapon  # adjust if different

def run_detection(video_source=0):
    """
    Generator function that yields (frame, alerts) tuples.
    Alerts include crowd size, fight, weapon, etc.
    """

    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video source: {video_source}")

    print("[INFO] Detection stream started...")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[INFO] End of video or read error.")
            break

        alerts = {
            "crowd": 0,
            "fight": False,
            "weapon": False,
            "group_id": None,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        # 🧍 Crowd detection
        try:
            crowd_count = detect_crowd(frame)
            alerts["crowd"] = crowd_count
            if crowd_count > 5:
                alerts["group_id"] = f"group-{int(time.time())}"
        except Exception as e:
            print("[WARN] Crowd detection failed:", e)

        # 🥊 Fight detection
        try:
            fight_detected = detect_fight(frame)
            alerts["fight"] = bool(fight_detected)
        except Exception as e:
            print("[WARN] Fight detection failed:", e)

        # 🔫 Weapon detection
        try:
            weapon_detected = detect_weapon(frame)
            alerts["weapon"] = bool(weapon_detected)
        except Exception as e:
            print("[WARN] Weapon detection failed:", e)

        # (Optional) overlay results on the frame
        cv2.putText(frame, f"Crowd: {alerts['crowd']}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        if alerts["fight"]:
            cv2.putText(frame, "FIGHT DETECTED", (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        if alerts["weapon"]:
            cv2.putText(frame, "WEAPON DETECTED", (10, 110),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        yield frame, alerts
        time.sleep(0.05)

    cap.release()
    print("[INFO] Detection stream stopped.")
