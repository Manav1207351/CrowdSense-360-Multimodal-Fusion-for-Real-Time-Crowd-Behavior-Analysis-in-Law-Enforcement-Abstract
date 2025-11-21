# src/trackers/bytetrack_wrapper.py
# Minimal wrapper interface so you can replace with ByteTrack later.
class SimpleTrackerWrapper:
    def __init__(self):
        # internal storage for tracked objects
        self.tracks = {}

    def update(self, detections):
        # detections: list of [x1,y1,x2,y2,score,label]
        # Return list of tracks: dict with id,bbox,label
        out = []
        for i,det in enumerate(detections):
            out.append({"id": i, "bbox": det[:4], "score": det[4], "label": det[5]})
        return out
