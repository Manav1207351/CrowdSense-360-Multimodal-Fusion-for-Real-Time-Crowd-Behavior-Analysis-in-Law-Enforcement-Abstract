"""
Quick test script to validate detection improvements
Run this to check if models load and basic detection works
"""
import cv2
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from src.detector.yolo_loader import load_yolo_models
from src.detector.config import load_config

def test_detection():
    print("="*60)
    print("🧪 DETECTION SYSTEM TEST")
    print("="*60)
    
    # Load config
    print("\n📋 Loading configuration...")
    cfg = load_config()
    print(f"   Video source: {cfg.get('video_source')}")
    print(f"   Detection conf: {cfg['thresholds']['detection_conf']}")
    print(f"   Weapon conf: {cfg['thresholds']['weapon_conf']}")
    print(f"   Fight conf: {cfg['thresholds']['fight_conf']}")
    
    # Load models
    print("\n🤖 Loading YOLO models...")
    try:
        crowd_yolo, knife_yolo, weapon_yolo, fight_model = load_yolo_models(cfg)
        print("   ✅ Crowd model loaded" if crowd_yolo else "   ❌ Crowd model failed")
        print("   ✅ Knife model loaded" if knife_yolo else "   ❌ Knife model failed")
        print("   ✅ Weapon model loaded" if weapon_yolo else "   ❌ Weapon model failed")
        print("   ✅ Fight model loaded" if fight_model else "   ❌ Fight model failed")
    except Exception as e:
        print(f"   ❌ Model loading failed: {e}")
        return False
    
    # Test video source
    print("\n📹 Testing video source...")
    video_src = cfg.get("video_source", 0)
    cap = cv2.VideoCapture(video_src)
    
    if not cap.isOpened():
        print(f"   ❌ Cannot open video source: {video_src}")
        return False
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"   ✅ Video opened successfully")
    print(f"   Frames: {total_frames}, FPS: {fps}, Resolution: {width}x{height}")
    
    # Test single frame detection
    print("\n🔍 Testing detection on first frame...")
    ret, frame = cap.read()
    if not ret:
        print("   ❌ Cannot read frame")
        cap.release()
        return False
    
    # Test person detection
    if crowd_yolo:
        results = crowd_yolo.predict(frame, conf=cfg['thresholds']['detection_conf'], verbose=False)
        person_count = 0
        for r in results:
            if hasattr(r, 'boxes'):
                person_count = len(r.boxes.xyxy)
        print(f"   👥 Detected {person_count} people")
    
    # Test knife detection
    if knife_yolo:
        knife_conf = max(0.3, cfg['thresholds']['weapon_conf'] - 0.15)
        results = knife_yolo.predict(frame, conf=knife_conf, verbose=False)
        knife_count = 0
        for r in results:
            if hasattr(r, 'boxes'):
                knife_count = len(r.boxes.xyxy)
        print(f"   🔪 Detected {knife_count} knives (threshold: {knife_conf:.2f})")
    
    # Test weapon detection
    if weapon_yolo:
        results = weapon_yolo.predict(frame, conf=cfg['thresholds']['weapon_conf'], verbose=False)
        weapon_count = 0
        for r in results:
            if hasattr(r, 'boxes'):
                weapon_count = len(r.boxes.xyxy)
        print(f"   🔫 Detected {weapon_count} weapons")
    
    cap.release()
    
    print("\n" + "="*60)
    print("✅ TEST COMPLETE - System ready for detection")
    print("="*60)
    print("\nTo run full detection, execute:")
    print("   python src/detector/infer_detector.py")
    return True

if __name__ == "__main__":
    success = test_detection()
    sys.exit(0 if success else 1)
