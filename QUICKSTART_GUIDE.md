# Quick Start Guide - CrowdSense 360

## Prerequisites
- Python 3.8+
- Node.js 16+
- All model files in `A:/src1/models/`

## Step 1: Install Backend Dependencies
```powershell
pip install flask flask-cors flask-socketio opencv-python ultralytics scipy numpy openpyxl
```

## Step 2: Install Frontend Dependencies
```powershell
cd frontend
npm install
```

## Step 3: Start the Flask Backend
```powershell
# From project root
python src/app.py
```
Server will start at: `http://localhost:5000`

## Step 4: Start the Frontend
```powershell
# In a new terminal
cd frontend
npm run dev
```
Dashboard will open at: `http://localhost:5173`

## Step 5: Run the Detector
```powershell
# In a new terminal, from project root
python src/detector/infer_detector.py
```

## What to Expect

### Console Output
```
🔄 Loading Models...
✅ Crowd YOLO Loaded
✅ Knife YOLO Loaded
✅ Weapon YOLO Loaded
✅ Fight Classifier Loaded
✅ Excel log initialized at: outputs/alerts_log.xlsx
🎥 Starting CrowdSense360...
```

### When Alerts Trigger
```
🔫 Weapon Alert
📝 Logged to Excel: Weapon Detected at 2025-11-21 10:30:45
📡 Broadcasted alert via WebSocket: weapon
```

### Files Created
- `outputs/alerts_log.xlsx` - Excel log of all alerts
- `outputs/alerts/*.jpg` - Screenshots of detections
- `alerts/*.json` - JSON files for each alert

## Frontend Features

### Left Panel (Sidebar)
- Camera list
- Select active camera

### Main Area
- 2 camera feeds (side by side)
- Event timeline at bottom

### Right Panel (Alerts)
- Live alert feed
- Filter by severity (ALL/HIGH/MED/LOW)
- Shows last 20 alerts
- Auto-updates in real-time

### Alert Information
- 🔫 Weapon / 🔪 Knife / 🥊 Fight / 👥 Crowd
- Timestamp
- Camera name
- Confidence % (for weapon/fight)
- People count (for crowd)
- Severity badge

## Configuration

Edit `src/detector/config.yaml`:

```yaml
# Change video source
video_source: "path/to/your/video.mp4"
# or use camera index
video_source: 0

# Adjust thresholds
thresholds:
  detection_conf: 0.35
  weapon_conf: 0.4
  fight_conf: 0.5

# Crowd alert parameters
people:
  group_threshold: 5        # Minimum people
  group_persist_seconds: 120  # 2 minutes
```

## Troubleshooting

### Models Not Loading
- Verify paths in `config.yaml`
- Check files exist at `A:/src1/models/`

### No WebSocket Connection
- Ensure Flask server is running on port 5000
- Check browser console for errors
- Verify `flask-socketio` is installed

### No Alerts Appearing
- Check console for detection logs
- Verify confidence thresholds aren't too high
- Ensure video source is valid

### Excel File Not Created
- Check `openpyxl` is installed
- Verify write permissions in `outputs/` directory

## Testing the System

### Test Weapon Detection
- Point camera at weapon-like object
- Should trigger within seconds if confidence > 0.4

### Test Fight Detection  
- Show fighting movements
- Requires person detection + fight behavior

### Test Crowd Alert
- Have 5+ people stay in frame
- Wait for 2 minutes
- Alert triggers when duration reached

## Stopping the System

1. Press `q` in detector window to stop detection
2. Press `Ctrl+C` in Flask terminal
3. Press `Ctrl+C` in frontend terminal

## Next Steps

- Adjust detection thresholds in config.yaml
- Review Excel log: `outputs/alerts_log.xlsx`
- Check screenshots in: `outputs/alerts/`
- Monitor real-time alerts in frontend

## Support

Check `INTEGRATION_SUMMARY.md` for detailed documentation.
