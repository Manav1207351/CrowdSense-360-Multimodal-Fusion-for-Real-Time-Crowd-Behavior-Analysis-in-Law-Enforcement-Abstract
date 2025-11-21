# src/utils/split_videos_to_dataset.py
import cv2
import os
import random
import shutil
from sklearn.model_selection import train_test_split

def extract_frames_from_videos(video_dir, output_dir, frame_interval=10, val_ratio=0.2):
    """
    Extracts frames from all videos in a directory and splits them into train/val sets.
    Each extracted frame will later be manually labeled using LabelImg or Roboflow.
    """
    images_dir = os.path.join(output_dir, "images")
    labels_dir = os.path.join(output_dir, "labels")

    for d in [images_dir, labels_dir]:
        os.makedirs(os.path.join(d, "train"), exist_ok=True)
        os.makedirs(os.path.join(d, "val"), exist_ok=True)

    all_frames = []
    for filename in os.listdir(video_dir):
        if not filename.lower().endswith(('.mp4', '.avi', '.mov')):
            continue

        video_path = os.path.join(video_dir, filename)
        cap = cv2.VideoCapture(video_path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_name = os.path.splitext(filename)[0]

        i = 0
        frame_id = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if i % frame_interval == 0:
                frame_name = f"{video_name}_frame_{frame_id}.jpg"
                frame_path = os.path.join(images_dir, frame_name)
                cv2.imwrite(frame_path, frame)
                all_frames.append(frame_name)
                frame_id += 1
            i += 1
        cap.release()

    # Split into train and val
    train_files, val_files = train_test_split(all_frames, test_size=val_ratio, random_state=42)

    for f in train_files:
        shutil.move(os.path.join(images_dir, f), os.path.join(images_dir, "train", f))
    for f in val_files:
        shutil.move(os.path.join(images_dir, f), os.path.join(images_dir, "val", f))

    print(f"✅ Extracted {len(all_frames)} frames.")
    print(f"Train: {len(train_files)} | Val: {len(val_files)}")

if __name__ == "__main__":
    extract_frames_from_videos(
        video_dir="E:\Crwoed\Dataset\SCVD_converted_sec_split\Weaponized",         # path where your input videos are
        output_dir="D:/CrowedSense 360/datasets/Weapons",          # where to store output images
        frame_interval=10,                    # take 1 frame every 10 frames
        val_ratio=0.2
    )

