# ============================================
# CrowdSense 360 - Quick Start Guide
# ============================================

## ✅ Your Trained Models (Already in Place)
- Crowd Detection: A:\src\src\detectors\models\crowd_yolo6\weights\best.pt
- Fight Detection: A:\src\src\detectors\models\fight_yolo\weights\best.pt
- Weapon Detection: A:\src\src\detectors\models\weapon_yolo2\weights\weapon_yolo.pt

## 🚀 How to Run

### 1. Start Backend (Port 8080)
```powershell
cd a:\src\src
python app.py
```

### 2. Start Frontend (Port 3000)
```powershell
cd a:\src\frontend
npm run dev
```

### 3. Access Dashboard
Open browser: http://localhost:3000

## 📤 How It Works

1. **Upload Video**: Click "Upload Video" button on any camera tile
2. **Backend Processing**: Video sent to `POST http://localhost:8080/api/detect`
3. **Detection**: Your trained models detect crowd/fight/weapon
4. **Results Display**: Frontend shows alerts in real-time
5. **Camera Status**: Camera goes ONLINE after upload

## 🎯 Detection Flow

```
Frontend (React) → Upload Video → Backend (Flask on port 8080)
                                      ↓
                          Load Your Trained YOLO Models
                                      ↓
                          Run Detection (Crowd/Fight/Weapon)
                                      ↓
Frontend ← JSON Response ← Backend Returns Results
```

## 📊 API Response Format

```json
{
  "status": "success",
  "camera_id": "Cam-1",
  "crowd": true,
  "fight": false,
  "weapon": false,
  "count": 25,
  "flow": 7,
  "crowd_severity": "high"
}
```

## ✨ Features

- ✅ All cameras start OFFLINE
- ✅ Upload video to activate camera (goes ONLINE)
- ✅ Real-time detection using YOUR trained models
- ✅ Alerts panel shows crowd/fight/weapon detections
- ✅ Severity color coding (HIGH/MED/LOW)
- ✅ Clean camera labels (Camera 1, 2, 3, 4)

## 🛠️ Troubleshooting

**Backend won't start?**
- Install dependencies: `pip install -r requirements.txt`
- Check if port 8080 is available

**Frontend won't start?**
- Install dependencies: `cd frontend && npm install`
- Check if port 3000 is available

**Models not loading?**
- Verify model paths in `a:\src\src\detectors\detectors.py`
- Check lines 9-11 for model paths
