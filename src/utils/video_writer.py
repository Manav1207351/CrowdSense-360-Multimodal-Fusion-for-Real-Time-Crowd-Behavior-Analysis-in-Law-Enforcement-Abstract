# src/utils/video_writer.py
import cv2
from pathlib import Path
class VideoWriter:
    def __init__(self, out_path, fourcc="mp4v", fps=20, size=(640,480)):
        Path = __import__("pathlib").Path
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        fourcc_code = cv2.VideoWriter_fourcc(*fourcc)
        self.writer = cv2.VideoWriter(out_path, fourcc_code, fps, size)

    def write(self, frame):
        self.writer.write(frame)

    def release(self):
        self.writer.release()
