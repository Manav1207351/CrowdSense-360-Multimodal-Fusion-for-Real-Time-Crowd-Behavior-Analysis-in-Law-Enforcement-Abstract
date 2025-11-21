# Demonstration: run plate detection (you can use the YOLO detector with "license_plate" class)
# This script expects you to run detection first (or run the detector inside this script)
import cv2, argparse
import easyocr
from ultralytics import YOLO

def main(args):
    model = YOLO(args.weights)
    reader = easyocr.Reader(['en'], gpu=False)
    cap = cv2.VideoCapture(args.video)
    while True:
        ret, frame = cap.read()
        if not ret: break
        res = model.predict(frame, imgsz=1024, verbose=False)[0]
        if hasattr(res, "boxes") and len(res.boxes):
            for b in res.boxes:
                cls = int(b.cls.cpu().numpy())
                conf = float(b.conf.cpu().numpy())
                if conf < args.conf_thresh: continue
                # assume license_plate class id provided in args
                if cls == args.plate_class:
                    x1,y1,x2,y2 = map(int, b.xyxy.cpu().numpy().reshape(-1))
                    crop = frame[y1:y2, x1:x2]
                    if crop.size:
                        txts = reader.readtext(crop, detail=0)
                        if txts:
                            cv2.putText(frame, txts[0], (x1, y1-6), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)
                    cv2.rectangle(frame, (x1,y1),(x2,y2),(0,255,255),2)
        cv2.imshow("PlateOCR", frame)
        if cv2.waitKey(1) == 27: break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--video", default="data/samples/test_video.mp4")
    p.add_argument("--weights", default="yolov8n.pt")
    p.add_argument("--plate_class", type=int, default=4)
    p.add_argument("--conf_thresh", type=float, default=0.35)
    args = p.parse_args()
    main(args)
