# src/detectors/infer_detector.py

import cv2
import time
import os
import json
import threading
import platform
from pathlib import Path
from datetime import datetime
from ultralytics import YOLO
import yaml
import requests
import numpy as np
import openpyxl
from openpyxl import Workbook

# Attempt winsound on Windows for nicer beep
try:
    import winsound
except Exception:
    winsound = None

ROOT = Path(__file__).resolve().parents[2]

# Add src to path for imports
import sys
sys.path.insert(0, str(ROOT))

# --------------------- Local Imports ---------------------
from src.detector.yolo_loader import load_yolo
from src.detector.fight_classifier import FightClassifier
from src.detector.behaviour_logic import group_alert_needed, is_night
# NOTE: GroupTracker implemented below (integrated)
from src.detector.group_detector import CrowdGroupDetector  # not used; integrated GroupManager below


# --------------------- Simple Tracker ---------------------
class SimpleCentroidTracker:
    def __init__(self, max_disappear=50, max_distance=120):
        self.next_id = 0
        self.objects = {}         # oid -> (cX, cY)
        self.disappeared = {}     # oid -> frames disappeared
        self.last_centroid = {}   # oid -> last centroid
        self.max_disappear = max_disappear
        self.max_distance = max_distance

    def register(self, centroid):
        oid = self.next_id
        self.objects[oid] = centroid
        self.disappeared[oid] = 0
        self.last_centroid[oid] = centroid
        self.next_id += 1

    def deregister(self, oid):
        self.objects.pop(oid, None)
        self.disappeared.pop(oid, None)
        self.last_centroid.pop(oid, None)

    def update(self, rects):
        """
        rects: list of (x1,y1,x2,y2)
        returns self.objects mapping
        """
        import math
        if len(rects) == 0:
            for oid in list(self.disappeared.keys()):
                self.disappeared[oid] += 1
                if self.disappeared[oid] > self.max_disappear:
                    self.deregister(oid)
            return self.objects

        input_centroids = []
        for (x1, y1, x2, y2) in rects:
            cX = int((x1 + x2) / 2)
            cY = int((y1 + y2) / 2)
            input_centroids.append((cX, cY))

        if len(self.objects) == 0:
            for c in input_centroids:
                self.register(c)
        else:
            oids = list(self.objects.keys())
            ocent = list(self.objects.values())
            used_input = set()
            for i, oid in enumerate(oids):
                best_j = None
                best_d = 1e9
                for j, ic in enumerate(input_centroids):
                    if j in used_input:
                        continue
                    d = math.hypot(ic[0] - ocent[i][0], ic[1] - ocent[i][1])
                    if d < best_d:
                        best_d = d
                        best_j = j
                if best_j is not None and best_d < self.max_distance:
                    self.objects[oid] = input_centroids[best_j]
                    self.disappeared[oid] = 0
                    used_input.add(best_j)
                else:
                    self.disappeared[oid] += 1
                    if self.disappeared[oid] > self.max_disappear:
                        self.deregister(oid)

            for j, ic in enumerate(input_centroids):
                if j not in used_input:
                    self.register(ic)

        return self.objects

    def get_stationary(self, movement_threshold=15, stationary_seconds=300):
        import math
        stationary = []
        for oid, cent in self.objects.items():
            last = self.last_centroid.get(oid, cent)
            dist = math.hypot(cent[0] - last[0], cent[1] - last[1])
            if dist <= movement_threshold:
                stationary.append(oid)
            self.last_centroid[oid] = cent
        return stationary

    def get_oid_centroids(self):
        """Return copy of current objects mapping"""
        return dict(self.objects)


# --------------------- Group Manager (multi-group) ---------------------
class GroupManager:
    """
    Maintain multiple groups (clusters) of people based on centroid proximity.
    Each group has:
      - id
      - member_oids (set)
      - start_time
      - last_seen
      - completed (bool)
      - count (latest)
      - bbox (optional)
    """
    def __init__(self, min_people=10, duration_sec=300, cluster_dist=120, vanish_timeout=10):
        self.min_people = min_people
        self.duration_sec = duration_sec
        self.cluster_dist = cluster_dist
        self.vanish_timeout = vanish_timeout
        self._next_id = 0
        self.groups = {}  # gid -> group dict

    def _cluster_oids(self, oid_centroids):
        """
        oid_centroids: dict oid->(x,y)
        returns list of clusters: list of sets of oids
        uses simple adjacency graph + DFS (distance threshold)
        """
        oids = list(oid_centroids.keys())
        if not oids:
            return []

        # build adjacency
        adj = {oid: set() for oid in oids}
        for i in range(len(oids)):
            for j in range(i+1, len(oids)):
                a = oids[i]; b = oids[j]
                ax, ay = oid_centroids[a]; bx, by = oid_centroids[b]
                if (ax - bx) ** 2 + (ay - by) ** 2 <= self.cluster_dist ** 2:
                    adj[a].add(b); adj[b].add(a)

        # connected components
        visited = set()
        clusters = []
        for oid in oids:
            if oid in visited:
                continue
            stack = [oid]
            comp = set()
            while stack:
                v = stack.pop()
                if v in visited:
                    continue
                visited.add(v)
                comp.add(v)
                for nb in adj[v]:
                    if nb not in visited:
                        stack.append(nb)
            clusters.append(comp)
        return clusters

    def update(self, oid_centroids, oid_to_bbox):
        """
        Call every frame with current centroid map and mapping from oid->bbox (if available).
        Returns:
          completed_events: list of group dicts that completed RIGHT NOW (one-time)
          active_groups: list of active group dicts
        """
        now = time.time()
        completed_events = []

        # cluster current oids
        clusters = self._cluster_oids(oid_centroids)

        # Filter clusters by size threshold
        candidate_clusters = [c for c in clusters if len(c) >= self.min_people]

        # For existing groups, mark as not-updated; we'll set updated=True if matched to a cluster
        for gid, g in list(self.groups.items()):
            g["updated"] = False

        # Match clusters to groups by overlap of member oids
        for cluster in candidate_clusters:
            # Try find best overlapping existing group
            best_gid = None
            best_overlap = 0
            for gid, g in self.groups.items():
                overlap = len(cluster & g["members"])
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_gid = gid

            if best_gid is not None and best_overlap > 0:
                # update existing group
                g = self.groups[best_gid]
                g["members"] = set(cluster)
                g["last_seen"] = now
                g["count"] = len(cluster)
                g["updated"] = True
                # update bbox
                g["bbox"] = self._compute_bbox_for_members(cluster, oid_to_bbox)
                # if not completed yet, check time
                if not g.get("completed", False):
                    elapsed = now - g["start_time"]
                    if elapsed >= self.duration_sec:
                        g["completed"] = True
                        g["duration_sec"] = self.duration_sec
                        completed_events.append(g.copy())
                continue

            # no matching group -> create new group
            self._next_id += 1
            gid = self._next_id
            group = {
                "id": gid,
                "members": set(cluster),
                "start_time": now,
                "last_seen": now,
                "count": len(cluster),
                "completed": False,
                "bbox": self._compute_bbox_for_members(cluster, oid_to_bbox),
                "updated": True
            }
            self.groups[gid] = group
            # newly created group won't be completed immediately (elapsed near 0)

        # Clean up groups not updated: if last_seen older than vanish_timeout, remove
        for gid, g in list(self.groups.items()):
            if not g.get("updated", True):
                if (now - g["last_seen"]) > self.vanish_timeout:
                    # remove group
                    self.groups.pop(gid, None)

        # Return completed events and active groups
        active = list(self.groups.values())
        return completed_events, active

    def _compute_bbox_for_members(self, members, oid_to_bbox):
        """
        members: set of oids
        oid_to_bbox: mapping oid->(x1,y1,x2,y2) or missing
        returns bbox [x1,y1,x2,y2] covering all available member boxes or None
        """
        xs = []
        ys = []
        xs2 = []
        ys2 = []
        for oid in members:
            if oid in oid_to_bbox and oid_to_bbox[oid] is not None:
                x1,y1,x2,y2 = oid_to_bbox[oid]
                xs.append(x1); ys.append(y1); xs2.append(x2); ys2.append(y2)
        if not xs:
            return None
        x1 = min(xs); y1 = min(ys); x2 = max(xs2); y2 = max(ys2)
        return [x1,y1,x2,y2]

    def get_active_groups(self):
        return list(self.groups.values())


# --------------------- Helpers ---------------------
def load_cfg():
    p = ROOT / "src" / "detector" / "config.yaml"
    with open(p, "r") as f:
        return yaml.safe_load(f)


def save_screenshot(frame, outdir, prefix="alert"):
    Path(outdir).mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fn = Path(outdir) / f"{prefix}_{ts}.jpg"
    cv2.imwrite(str(fn), frame)
    return str(fn)


def save_cropped_group(frame, bbox, outdir, prefix="group"):
    """
    bbox: [x1,y1,x2,y2] - will clip to frame bounds and add small padding
    """
    if bbox is None:
        return save_screenshot(frame, outdir, prefix=prefix)
    h, w = frame.shape[:2]
    x1,y1,x2,y2 = bbox
    pad = 10
    x1 = max(0, x1 - pad); y1 = max(0, y1 - pad)
    x2 = min(w-1, x2 + pad); y2 = min(h-1, y2 + pad)
    crop = frame[y1:y2, x1:x2]
    if crop.size == 0:
        return save_screenshot(frame, outdir, prefix=prefix)
    Path(outdir).mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fn = Path(outdir) / f"{prefix}_{ts}.jpg"
    cv2.imwrite(str(fn), crop)
    return str(fn)


def post_alert(cfg, payload, image_path=None):
    if not cfg.get("alerting", {}).get("enable_http", False):
        return False

    url = cfg["alerting"]["http_endpoint"]
    headers = {}

    if cfg["alerting"].get("api_key"):
        headers["Authorization"] = f"Bearer {cfg['alerting']['api_key']}"

    files = {}
    try:
        if image_path and Path(image_path).exists():
            files["image"] = open(image_path, "rb")
            r = requests.post(url, data={"json": json.dumps(payload)}, headers=headers, files=files, timeout=8)
        else:
            r = requests.post(url, json=payload, headers=headers, timeout=8)
        return r.status_code == 200
    except Exception as e:
        print("Failed to post alert:", e)
        return False


# --------------------- EXCEL LOGGING ---------------------
def init_excel_log(excel_path):
    """Initialize Excel file with headers if it doesn't exist"""
    if not Path(excel_path).exists():
        wb = Workbook()
        ws = wb.active
        ws.title = "Alerts"
        ws.append(["Timestamp", "Detection Type", "Camera Source", "People Count", "Confidence", "Details"])
        wb.save(excel_path)
        print(f"✅ Excel log initialized at: {excel_path}")
    return excel_path


def log_to_excel(excel_path, timestamp, detection_type, camera_source, people_count=0, confidence=0.0, details=""):
    """Log alert to Excel sheet"""
    try:
        wb = openpyxl.load_workbook(excel_path)
        ws = wb.active
        ws.append([
            timestamp,
            detection_type,
            camera_source,
            people_count,
            f"{confidence:.2f}" if confidence > 0 else "",
            details
        ])
        wb.save(excel_path)
        print(f"📝 Logged to Excel: {detection_type} at {timestamp}")
        return True
    except Exception as e:
        print(f"❌ Failed to log to Excel: {e}")
        return False


# --------------------- HUD Drawing & UI helpers ---------------------
def format_seconds(s):
    s = int(s)
    m = s // 60
    sec = s % 60
    return f"{m:02d}:{sec:02d}"


def gid_to_color(gid):
    """
    Convert Group ID to a deterministic color (BGR) using HSV mapping.
    """
    if gid <= 0:
        return (255, 255, 255)
    # hue range for OpenCV HSV: 0-179
    hue = (gid * 37) % 180
    hsv = np.uint8([[[hue, 200, 255]]])  # S=200, V=255
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0][0]
    return (int(bgr[0]), int(bgr[1]), int(bgr[2]))


def draw_hud(frame, weapon_state, fight_state, crowd_count, groups_active, crowd_threshold=10, hud_width=380, hud_pad=8, raw_count=None):
    """
    Draw top-left HUD with:
      - weapon_state, fight_state dicts
      - crowd_count int (smoothed)
      - raw_count int (optional, for debugging)
      - groups_active: list of group dicts (show up to 3)
    """
    h, w = frame.shape[:2]
    x0, y0 = 10, 10
    x1 = x0 + hud_width
    # lines: weapon, fight, crowd, group lines (up to 3)
    max_groups_show = 3
    line_h = 22
    lines = 3 + max_groups_show
    panel_h = line_h * lines + hud_pad * 2

    overlay = frame.copy()
    cv2.rectangle(overlay, (x0, y0), (x1, y0 + panel_h), (0, 0, 0), -1)
    alpha = 0.5
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    cv2.rectangle(frame, (x0, y0), (x1, y0 + panel_h), (200, 200, 200), 1)

    tx = x0 + hud_pad
    ty = y0 + hud_pad + 16

    # Weapon
    if weapon_state.get("detected", False):
        weapon_text = f"🔫 Weapon: DETECTED {weapon_state.get('conf', 0):.2f}"
        weapon_color = (0, 0, 255)
    else:
        weapon_text = "🔫 Weapon: SAFE"
        weapon_color = (0, 255, 0)
    cv2.putText(frame, weapon_text, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.55, weapon_color, 1)
    ty += line_h

    # Fight
    if fight_state.get("detected", False):
        fight_text = f"🥊 Fight: DETECTED {fight_state.get('conf', 0):.2f}"
        fight_color = (0, 255, 255)  # yellow-ish (BGR)
    else:
        fight_text = "🥊 Fight: SAFE"
        fight_color = (0, 255, 0)
    cv2.putText(frame, fight_text, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.55, fight_color, 1)
    ty += line_h

    # Crowd - show smoothed count (and optionally raw count for debugging)
    crowd_color = (0, 255, 255) if crowd_count >= crowd_threshold else (255, 255, 255)
    crowd_text = f"👥 Crowd: {crowd_count} people"
    if raw_count is not None and raw_count != crowd_count:
        crowd_text += f" (raw: {raw_count})"
    cv2.putText(frame, crowd_text, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.55, crowd_color, 1)
    ty += line_h

    # Groups (up to max_groups_show)
    shown = 0
    for g in (groups_active or []):
        if shown >= max_groups_show:
            break
        gid = g["id"]
        elapsed = int(time.time() - g["start_time"]) if not g.get("completed", False) else int(g.get("duration_sec", 300))
        total = g.get("duration_sec", 300)
        remaining = max(0, total - elapsed)
        timer_text = f"Group {gid}: {g['count']} ppl | {format_seconds(elapsed)} / {total}s ({format_seconds(remaining)} left)"
        color = gid_to_color(gid)
        cv2.putText(frame, timer_text, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.50, color, 1)
        ty += line_h
        shown += 1

    # if fewer than max, leave empty lines (spacing preserved)
    # nothing else to draw here


# --------------------- Utility: match oids -> rects ---------------------
def map_oids_to_rects(oid_centroids, rects):
    """
    rects: list of (x1,y1,x2,y2)
    return mapping oid->rect (choose nearest rect center)
    """
    oid_to_rect = {}
    if not oid_centroids or not rects:
        return oid_to_rect

    # precompute rect centers
    rect_centers = []
    for r in rects:
        x1,y1,x2,y2 = r
        rect_centers.append(((x1+x2)//2, (y1+y2)//2))

    for oid, cent in oid_centroids.items():
        best_j = None
        best_d = 1e9
        for j, rc in enumerate(rect_centers):
            d = (cent[0] - rc[0])**2 + (cent[1] - rc[1])**2
            if d < best_d:
                best_d = d
                best_j = j
        if best_j is not None:
            oid_to_rect[oid] = rects[best_j]
    return oid_to_rect


# --------------------- SOUND & ALERT HELPERS ---------------------
def play_weapon_sound_nonblocking():
    """Play a short weapon alert sound in a non-blocking thread. Fallbacks applied."""
    def _play():
        try:
            if winsound and platform.system().lower().startswith("win"):
                # frequency, duration(ms)
                winsound.Beep(1000, 450)
            else:
                # Try simple system bell as fallback
                print("\a", end="", flush=True)
        except Exception:
            try:
                print("\a", end="", flush=True)
            except Exception:
                pass

    t = threading.Thread(target=_play, daemon=True)
    t.start()


# --------------------- MAIN PIPELINE ---------------------
def main():
    cfg = load_cfg()
    device = cfg.get("device", "cpu")

    print("\n🔄 Loading Models...\n")
    
    # Load Crowd Detection Model
    crowd_yolo = None
    crowd_path = cfg["models"].get("crowd", "")
    if Path(crowd_path).exists():
        crowd_yolo = load_yolo(crowd_path, device=device)
        print("✅ Crowd YOLO Loaded")
    else:
        print(f"⚠ Crowd model NOT found at: {crowd_path}")

    # Load Weapon Detection Model  
    weapon_yolo = None
    weapon_path = cfg["models"].get("weapon", "")
    if Path(weapon_path).exists():
        weapon_yolo = load_yolo(weapon_path, device=device)
        print("✅ Weapon YOLO Loaded")
    else:
        print(f"⚠ Weapon model NOT found at: {weapon_path}")

    # Load Fight Classifier Model
    fight_model = None
    fight_path = cfg["models"].get("fight", "")
    if Path(fight_path).exists():
        fight_model = FightClassifier(fight_path, device=device)
        print("✅ Fight Classifier Loaded")
    else:
        print(f"⚠ Fight model NOT found at: {fight_path}")

    # Video Source
    src = cfg.get("video_source", 0)
    cap = cv2.VideoCapture(src)
    
    # Increase tracker stability - longer persistence, larger distance threshold
    tracker = SimpleCentroidTracker(max_disappear=200, max_distance=300)

    # Group manager: updated parameters for 5+ people for 2+ minutes (120 seconds)
    group_threshold = cfg.get("people", {}).get("group_threshold", 5)
    group_duration = cfg.get("people", {}).get("group_persist_seconds", 120)
    group_manager = GroupManager(min_people=group_threshold, duration_sec=group_duration, cluster_dist=120, vanish_timeout=10)

    out_dir = ROOT / cfg.get("output_dir", "outputs")
    shot_dir = ROOT / cfg.get("alert_screenshot_dir", "outputs/alerts")
    out_dir.mkdir(parents=True, exist_ok=True)
    shot_dir.mkdir(parents=True, exist_ok=True)

    # Initialize Excel logging
    excel_path = out_dir / "alerts_log.xlsx"
    init_excel_log(excel_path)
    
    # Get camera source name for logging
    camera_source = cfg.get("video_source", "Camera-1")
    if isinstance(camera_source, int):
        camera_source = f"Camera-{camera_source}"
    elif "/" in str(camera_source) or "\\" in str(camera_source):
        camera_source = Path(camera_source).stem  # Use filename without extension

    # HUD detection state
    HUD_FADE_SEC = 5.0  # keep weapon/fight indicator visible for this many seconds after detection
    weapon_state = {"detected": False, "ts": 0.0, "conf": 0.0, "last_beep": 0.0}
    fight_state = {"detected": False, "ts": 0.0, "conf": 0.0}
    
    # Detection smoothing - reduce fluctuation by averaging over recent frames
    from collections import deque
    person_count_window = deque(maxlen=15)  # Average over last 15 frames (~0.5 sec at 30fps)
    weapon_count_window = deque(maxlen=10)

    print("\n🎥 Starting CrowdSense360...\n")

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ No frame - check video source.")
            break

        frame_count += 1
        now = datetime.now()
        hour = now.hour

        # Run YOLO detection (crowd model for person detection) - using lower threshold for better detection
        detection_threshold = max(0.2, cfg["thresholds"]["detection_conf"] - 0.1)
        results = crowd_yolo.predict(frame, imgsz=640, conf=detection_threshold, device=device, verbose=False) if crowd_yolo else []

        persons = []
        dets_all = []
        # We'll collect person rects to map to oids later
        for r in results:
            if not hasattr(r, "boxes"):
                continue

            boxes = r.boxes.xyxy.cpu().numpy()
            confs = r.boxes.conf.cpu().numpy()
            classes = r.boxes.cls.cpu().numpy().astype(int)
            names = getattr(crowd_yolo, "names", {}) if crowd_yolo else {}

            for box, conf, cls in zip(boxes, confs, classes):
                x1, y1, x2, y2 = map(int, box)
                label = names.get(cls, str(cls))
                dets_all.append((x1, y1, x2, y2, float(conf), label))
                if label.lower() == "person" or cls == 0:
                    persons.append((x1, y1, x2, y2))

        # Update tracker with detected person rects
        tracker.update(persons)
        stationary = tracker.get_stationary()
        oid_centroids = tracker.get_oid_centroids()
        
        # Add smoothing for person count to reduce fluctuation
        raw_person_count = len(oid_centroids)
        person_count_window.append(raw_person_count)
        num_people = int(sum(person_count_window) / len(person_count_window))  # Rolling average
        
        # Debug output every 30 frames
        if frame_count % 30 == 0:
            print(f"Frame {frame_count}: Raw={raw_person_count}, Smoothed={num_people} people")

        # Map oids -> rects (for cropping group images)
        oid_to_rect = map_oids_to_rects(oid_centroids, persons)

        # ----------------- GROUP CLUSTERING + MANAGEMENT --------------------
        completed_groups, active_groups = group_manager.update(oid_centroids, oid_to_rect)
        # completed_groups: list of groups that just finished duration this frame
        # active_groups: list of active group dicts

        # Handle completed groups (save crop + alert)
        for g in completed_groups:
            gid = g["id"]
            print(f"🚨 Group {gid} completed {group_manager.duration_sec}s: saving and alerting.")
            bbox = g.get("bbox")
            # in case bbox is None, save full frame; else save cropped group area
            pth = save_cropped_group(frame, bbox, shot_dir, prefix=f"group_{gid}_5min")
            payload = {
                "type": "crowd_group_complete",
                "group_id": gid,
                "people_count": g.get("count", num_people),
                "duration_sec": group_manager.duration_sec,
                "time": now.isoformat(),
                "camera": camera_source
            }
            post_alert(cfg, payload, image_path=pth)
            
            # Log to Excel
            log_to_excel(
                excel_path,
                now.strftime("%Y-%m-%d %H:%M:%S"),
                "Crowd (5+ people for 2+ min)",
                camera_source,
                people_count=g.get("count", num_people),
                confidence=0.0,
                details=f"Group {gid} persisted for {group_manager.duration_sec}s"
            )

        # ----------------- Stationary group logic (legacy) -------------------
        if group_alert_needed(num_people, len(stationary), cfg, hour):
            pth = save_screenshot(frame, shot_dir, prefix="group_stationary")
            payload = {
                "type": "group_stationary",
                "time": now.isoformat(),
                "group_size": num_people,
                "stationary_count": len(stationary),
            }
            post_alert(cfg, payload, image_path=pth)
            print("🚨 Stationary Group Alert Sent")

        # ---------------- Weapon Detection ----------------
        weapon_boxes = []  # list of (x1,y1,x2,y2,conf)
        raw_weapon_count = 0
        if weapon_yolo:
            try:
                wres = weapon_yolo.predict(frame, imgsz=640, conf=cfg["thresholds"]["weapon_conf"], device=device, verbose=False)
                for r in wres:
                    if not hasattr(r, "boxes"):
                        continue
                    for box, conf, cls in zip(
                        r.boxes.xyxy.cpu().numpy(),
                        r.boxes.conf.cpu().numpy(),
                        r.boxes.cls.cpu().numpy().astype(int)
                    ):
                        x1, y1, x2, y2 = map(int, box)
                        raw_weapon_count += 1
                        crop = frame[max(0,y1):y2, max(0,x1):x2]
                        if crop.size == 0:
                            continue

                        # record weapon box for drawing
                        weapon_boxes.append((x1,y1,x2,y2,float(conf)))

                        # set HUD weapon state
                        weapon_state["detected"] = True
                        weapon_state["ts"] = time.time()
                        weapon_state["conf"] = float(conf)

                # Apply smoothing - only trigger alert if weapon detected in multiple consecutive frames
                weapon_count_window.append(raw_weapon_count)
                smoothed_weapon_count = sum(weapon_count_window) / len(weapon_count_window)
                
                # Only process alerts if smoothed count indicates stable detection (>0.1 means detected in >10% of recent frames)
                if smoothed_weapon_count > 0.1 and raw_weapon_count > 0:
                    print(f"⚠️  Raw weapon detections: {raw_weapon_count}, Smoothed: {smoothed_weapon_count:.2f}")
                
                # Only process alerts if smoothed count indicates stable detection (>0.1 means detected in >10% of recent frames)
                if smoothed_weapon_count > 0.1 and raw_weapon_count > 0:
                    for (x1,y1,x2,y2,conf) in weapon_boxes:
                        crop = frame[max(0,y1):y2, max(0,x1):x2]
                        
                        # Play weapon sound (but not on every frame — only if last beep > 1s)
                        if time.time() - weapon_state.get("last_beep", 0) > 1.0:
                            play_weapon_sound_nonblocking()
                            weapon_state["last_beep"] = time.time()

                        pth = save_screenshot(crop, shot_dir, prefix="weapon")
                        payload = {
                            "type": "weapon", 
                            "time": now.isoformat(), 
                            "confidence": float(conf),
                            "camera": camera_source
                        }
                        post_alert(cfg, payload, image_path=pth)
                        
                        # Log to Excel
                        log_to_excel(
                            excel_path,
                            now.strftime("%Y-%m-%d %H:%M:%S"),
                            "Weapon Detected",
                            camera_source,
                            people_count=0,
                            confidence=float(conf),
                            details=f"Weapon detection at conf={conf:.2f}"
                        )
                        
                        print(f"🔫 Weapon Alert (conf={conf:.2f})")
                        break  # Only send one alert per frame
                        
            except Exception as e:
                print("Weapon detection error:", e)

        # ---------------- Fight Detection ----------------
        fight_boxes = []  # list of (x1,y1,x2,y2,conf,oid) or (x1,y1,x2,y2,conf)
        if fight_model:
            try:
                # we'll run the classifier per tracked object (use oid_to_rect mapping)
                for oid, rect in oid_to_rect.items():
                    if rect is None:
                        continue
                    x1,y1,x2,y2 = rect
                    crop = frame[max(0,y1):y2, max(0,x1):x2]
                    if crop.size == 0:
                        continue
                    prob = fight_model.predict_from_frame(crop)
                    if prob >= cfg["thresholds"]["fight_conf"]:
                        fight_boxes.append((x1,y1,x2,y2,float(prob), oid))
                        # HUD fight state
                        fight_state["detected"] = True
                        fight_state["ts"] = time.time()
                        fight_state["conf"] = float(prob)
                        pth = save_screenshot(frame, shot_dir, prefix="fight")
                        payload = {
                            "type": "fight",
                            "time": now.isoformat(),
                            "confidence": float(prob),
                            "object_id": oid,
                            "camera": camera_source
                        }
                        post_alert(cfg, payload, image_path=pth)
                        
                        # Log to Excel
                        log_to_excel(
                            excel_path,
                            now.strftime("%Y-%m-%d %H:%M:%S"),
                            "Fight Detected",
                            camera_source,
                            people_count=0,
                            confidence=float(prob),
                            details=f"Fight detection on person ID {oid}"
                        )
                        
                        print("🥊 Fight Detected:", prob)
            except Exception as e:
                print("Fight detection error:", e)

        # fade out weapon/fight/knife indicators after HUD_FADE_SEC
        now_ts = time.time()
        if weapon_state["detected"] and (now_ts - weapon_state["ts"] > HUD_FADE_SEC):
            weapon_state["detected"] = False
            weapon_state["conf"] = 0.0

        if fight_state["detected"] and (now_ts - fight_state["ts"] > HUD_FADE_SEC):
            fight_state["detected"] = False
            fight_state["conf"] = 0.0

        # ---------------- DRAW DETECTIONS ----------------
        # Draw person boxes first (green)
        for (x1, y1, x2, y2, conf, label) in dets_all:
            if str(label).lower() == "person" or label == "0":
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 0), 2)
                cv2.putText(frame, f"person {conf:.2f}", (x1, max(15, y1 - 5)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

        # Draw weapon boxes in RED (top-left label) and also mark blinking border later
        for (x1,y1,x2,y2,conf) in weapon_boxes:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)  # BGR red
            cv2.putText(frame, f"weapon {conf:.2f}", (x1, max(15, y1 - 5)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1)

        # Draw fight boxes in YELLOW
        for (x1,y1,x2,y2,conf, oid) in fight_boxes:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)  # BGR yellow
            cv2.putText(frame, f"fight {conf:.2f}", (x1, max(15, y1 - 5)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)
            # optionally mark the oid
            cv2.putText(frame, f"ID{oid}", (x2 - 40, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0,255,255), 1)

        # draw tracker centroids
        for oid, cent in oid_centroids.items():
            cv2.circle(frame, (int(cent[0]), int(cent[1])), 4, (255, 0, 0), -1)
            cv2.putText(frame, f"ID{oid}", (int(cent[0]) + 5, int(cent[1]) + 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 0), 1)

        # Draw group bounding boxes (active groups) with unique color per group id
        for g in active_groups:
            bbox = g.get("bbox")
            gid = g["id"]
            color = gid_to_color(gid)
            if bbox:
                x1,y1,x2,y2 = bbox
                thickness = 2
                # If group completed, use a thicker green border
                if g.get("completed", False):
                    color = (0, 200, 0)
                    thickness = 3
                cv2.rectangle(frame, (x1,y1), (x2,y2), color, thickness)
                cv2.putText(frame, f"Group {gid} ({g['count']})", (x1, max(15, y1 - 6)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        # ------------------ BLINKING RED BORDER FOR WEAPON ALERT ------------------
        if weapon_state.get("detected", False):
            # blink at ~2Hz
            blink = int(time.time() * 2) % 2
            if blink == 1:
                h, w = frame.shape[:2]
                thickness = 6
                # draw red rectangle around entire frame
                cv2.rectangle(frame, (2, 2), (w-3, h-3), (0, 0, 255), thickness)

        # ------------------ FLASHING FIGHT BANNER (TOP-CENTER) ------------------
        if fight_state.get("detected", False):
            # flash at ~1Hz
            blink = int(time.time() * 1) % 2
            if blink == 1:
                text = "!!! FIGHT DETECTED !!!"
                font = cv2.FONT_HERSHEY_DUPLEX
                scale = 1.2
                thickness = 2
                (tw, th), _ = cv2.getTextSize(text, font, scale, thickness)
                h, w = frame.shape[:2]
                x = (w - tw) // 2
                y = 40
                # draw black background rectangle for readability
                cv2.rectangle(frame, (x-8, y-th-8), (x+tw+8, y+6), (0,0,0), -1)
                cv2.putText(frame, text, (x, y), font, scale, (0,255,255), thickness, cv2.LINE_AA)

        # Draw the top-left HUD (Option A) - show up to 3 groups with raw vs smoothed count
        draw_hud(frame, weapon_state, fight_state, num_people, active_groups, 
                 crowd_threshold=group_manager.min_people, raw_count=raw_person_count)

        cv2.imshow("CrowdSense360", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


# ---------------------
if __name__ == "__main__":
    main()
