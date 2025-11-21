import cv2
import os
from pathlib import Path

# Input video folders
SOURCE_DIRS = {
    "weapons": "D:/CrowedSense 360/Dataset/SCVD_converted_sec_split/Weaponized/",
    "fight": "D:/CrowedSense 360/Dataset/SCVD_converted_sec_split/Violence/",
    "normal": "D:/CrowedSense 360/Dataset/SCVD_converted_sec_split/Normal/"
}

# Output folder for extracted frames
OUTPUT_DIR = Path("video_frames")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Frame extraction rate (every N frames)
FRAME_INTERVAL = 30  # extract 1 frame per 30 frames (~1 sec for 30fps videos)

for class_name, folder in SOURCE_DIRS.items():
    out_dir = OUTPUT_DIR / class_name
    out_dir.mkdir(parents=True, exist_ok=True)

    videos = list(Path(folder).glob("*.mp4")) + list(Path(folder).glob("*.avi")) + list(Path(folder).glob("*.mov"))
    print(f"[INFO] Found {len(videos)} videos for class '{class_name}'")

    for vid_path in videos:
        cap = cv2.VideoCapture(str(vid_path))
        frame_idx = 0
        saved_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % FRAME_INTERVAL == 0:
                frame_filename = out_dir / f"{vid_path.stem}_frame{saved_idx}.jpg"
                cv2.imwrite(str(frame_filename), frame)
                saved_idx += 1

            frame_idx += 1

        cap.release()
        print(f"[INFO] Extracted {saved_idx} frames from {vid_path.name}")

print("✅ Frame extraction complete. Frames saved in:", OUTPUT_DIR)
