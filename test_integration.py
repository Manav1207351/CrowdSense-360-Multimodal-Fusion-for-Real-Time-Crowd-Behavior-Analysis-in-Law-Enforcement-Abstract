"""
Integration Test Script
Verifies frontend-backend integration and model loading
"""

import os
import sys

print("=" * 60)
print("🔍 CROWDSENSE 360 - INTEGRATION CHECK")
print("=" * 60)

# 1. Check model files exist
print("\n✅ Step 1: Checking trained model files...")
models = {
    "Crowd Model": "src/detectors/models/crowd_yolo6/weights/best.pt",
    "Fight Model": "src/detectors/models/fight_yolo/weights/best.pt",
    "Weapon Model": "src/detectors/models/weapon_yolo2/weights/weapon_yolo.pt"
}

all_models_exist = True
for name, path in models.items():
    full_path = os.path.join("A:/src", path)
    exists = os.path.exists(full_path)
    status = "✅ FOUND" if exists else "❌ MISSING"
    print(f"   {status}: {name}")
    if exists:
        size_mb = os.path.getsize(full_path) / (1024 * 1024)
        print(f"      Size: {size_mb:.2f} MB")
    all_models_exist = all_models_exist and exists

if not all_models_exist:
    print("\n❌ ERROR: Some models are missing!")
    sys.exit(1)

# 2. Check backend dependencies
print("\n✅ Step 2: Checking Python dependencies...")
required_packages = ['flask', 'flask_cors', 'cv2', 'ultralytics', 'numpy', 'scipy']
missing = []

for package in required_packages:
    try:
        __import__(package)
        print(f"   ✅ {package}")
    except ImportError:
        print(f"   ❌ {package} - NOT INSTALLED")
        missing.append(package)

if missing:
    print(f"\n❌ Install missing packages: pip install {' '.join(missing)}")
    sys.exit(1)

# 3. Check if models can be loaded
print("\n✅ Step 3: Testing model loading...")
try:
    from ultralytics import YOLO
    
    print("   Loading Crowd Model...")
    crowd = YOLO("src/detectors/models/crowd_yolo6/weights/best.pt")
    print("   ✅ Crowd Model loaded successfully")
    
    print("   Loading Fight Model...")
    fight = YOLO("src/detectors/models/fight_yolo/weights/best.pt")
    print("   ✅ Fight Model loaded successfully")
    
    print("   Loading Weapon Model...")
    weapon = YOLO("src/detectors/models/weapon_yolo2/weights/weapon_yolo.pt")
    print("   ✅ Weapon Model loaded successfully")
    
except Exception as e:
    print(f"   ❌ Error loading models: {e}")
    sys.exit(1)

# 4. Check frontend files
print("\n✅ Step 4: Checking frontend setup...")
frontend_files = [
    "frontend/package.json",
    "frontend/src/components/CameraTile.jsx",
    "frontend/src/pages/Dashboard.jsx"
]

for file in frontend_files:
    full_path = os.path.join("A:/src", file)
    exists = os.path.exists(full_path)
    status = "✅" if exists else "❌"
    print(f"   {status} {file}")

# 5. Check backend API endpoint
print("\n✅ Step 5: Checking backend configuration...")
backend_file = "A:/src/src/app.py"
if os.path.exists(backend_file):
    with open(backend_file, 'r', encoding='utf-8') as f:
        content = f.read()
        has_detect_endpoint = '/api/detect' in content
        has_cors = 'flask_cors' in content
        port_8080 = 'port=8080' in content
        
        print(f"   {'✅' if has_detect_endpoint else '❌'} /api/detect endpoint")
        print(f"   {'✅' if has_cors else '❌'} CORS enabled")
        print(f"   {'✅' if port_8080 else '❌'} Running on port 8080")
else:
    print("   ❌ app.py not found")

print("\n" + "=" * 60)
print("✅ INTEGRATION CHECK COMPLETE!")
print("=" * 60)
print("\n📋 NEXT STEPS:")
print("   1. Start Backend:  cd A:/src/src && python app.py")
print("   2. Start Frontend: cd A:/src/frontend && npm run dev")
print("   3. Open Browser:   http://localhost:3000")
print("\n💡 When you upload a video:")
print("   - Video is sent to: http://localhost:8080/api/detect")
print("   - Your trained models process the video")
print("   - Results appear in the alerts panel")
print("=" * 60)
