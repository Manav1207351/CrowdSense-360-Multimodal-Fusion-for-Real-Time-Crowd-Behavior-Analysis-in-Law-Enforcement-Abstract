# CrowdSense 360 - Integration Summary

## Overview
This document summarizes the complete integration of the new SRC models with real-time alert system, Excel logging, and frontend updates.

## 1. Model Integration

### Updated Model Paths (config.yaml)
All models now use local paths at `A:/src1/models/`:

- **Crowd Detection**: `A:/src1/models/crowd_yolo6/weights/best.pt`
- **Fight Detection**: `A:/src1/models/fight_yolo/weights/best.pt`
- **Knife Detection**: `A:/src1/models/weapon_yolo/weights/best.pt`
- **Weapon Detection**: `A:/src1/models/weapon4/weights/best.pt`

### Detection Parameters
- **Group Threshold**: 5 people (changed from 7)
- **Group Duration**: 120 seconds / 2 minutes (changed from 300s)
- **Detection Confidence**: 0.35
- **Weapon/Knife Confidence**: 0.4
- **Fight Confidence**: 0.5

## 2. Alert Trigger Conditions

The system now triggers alerts for three specific events:

### A. Weapon/Knife Detection
- **When**: Any weapon or knife is detected with confidence ≥ 0.4
- **Action**: 
  - Screenshot saved
  - Alert sent to backend API
  - Excel log updated
  - Real-time WebSocket broadcast
  - Audio beep played
  - Red blinking border on video feed

### B. Fight Detection
- **When**: Fight behavior detected with confidence ≥ 0.5
- **Action**:
  - Screenshot saved
  - Alert sent to backend API
  - Excel log updated
  - Real-time WebSocket broadcast
  - Yellow flashing banner on screen

### C. Crowd Persistence
- **When**: 5 or more people remain in same area for 2+ minutes
- **Action**:
  - Cropped group screenshot saved
  - Alert sent to backend API
  - Excel log updated with people count
  - Real-time WebSocket broadcast

## 3. Excel Logging System

### File Location
`outputs/alerts_log.xlsx` (created automatically)

### Log Columns
1. **Timestamp**: YYYY-MM-DD HH:MM:SS format
2. **Detection Type**: "Weapon Detected", "Knife Detected", "Fight Detected", or "Crowd (5+ people for 2+ min)"
3. **Camera Source**: Camera name or video file name
4. **People Count**: Number of people (for crowd alerts)
5. **Confidence**: Detection confidence score
6. **Details**: Additional information about the detection

### Features
- Auto-creates Excel file with headers on first run
- Thread-safe logging
- Appends new rows for each alert event
- Only logs when actual events occur (no continuous logging)

## 4. Backend Updates (Flask)

### New Dependencies
```python
flask-socketio  # Real-time WebSocket communication
openpyxl       # Excel file operations
```

### API Endpoints

#### POST /api/alerts
- Receives alert data from detector
- Saves JSON file locally
- Broadcasts to all connected WebSocket clients
- Returns success status

#### WebSocket Events
- **connect**: Client connected
- **disconnect**: Client disconnected  
- **new_alert**: Broadcast when new alert received

### Alert Payload Format
```json
{
  "type": "weapon|fight|crowd_group_complete",
  "time": "2025-11-21T10:30:45.123456",
  "camera": "Camera-1",
  "confidence": 0.85,
  "people_count": 7,
  "duration_sec": 120
}
```

## 5. Frontend Updates

### Camera Display
- **Changed from**: 4 cameras (2x2 grid)
- **Changed to**: 2 cameras (2x1 grid)
- Cameras 3 and 4 removed from `initialCameras.js`

### WebSocket Integration
- Replaced native WebSocket with Socket.IO client
- Auto-reconnection on disconnect
- Real-time alert reception and display

### Alert Panel Enhancements

#### Display Information
- **Detection Type**: Icon + label (🔫 Weapon, 🥊 Fight, 👥 Crowd)
- **Timestamp**: Formatted time display
- **Camera Name**: Shows camera source
- **People Count**: Displayed for crowd alerts
- **Confidence Score**: Shown as percentage for weapon/fight
- **Severity Badge**: HIGH, MED, or LOW

#### Alert Filtering
- ALL, HIGH, MED, LOW filter buttons
- Shows last 20 alerts
- Auto-updates on new alerts

## 6. Detection Visualization

### On-Screen Display (HUD)
Top-left panel shows:
- 🔫 Weapon status + confidence
- 🔪 Knife status + confidence  
- 🥊 Fight status + confidence
- 👥 Crowd count
- Up to 3 active groups with timers

### Visual Indicators
- **Person boxes**: Green rectangles
- **Weapon boxes**: Red rectangles
- **Knife boxes**: Orange rectangles
- **Fight boxes**: Yellow rectangles
- **Group boxes**: Color-coded by group ID
- **Weapon/Knife alert**: Red blinking border
- **Fight alert**: Yellow flashing banner

## 7. File Structure

```
src/
├── app.py (Flask + SocketIO server)
├── detector/
│   ├── config.yaml (model paths & thresholds)
│   ├── infer_detector.py (main detection logic)
│   ├── behaviour_logic.py (alert logic)
│   └── fight_classifier.py
frontend/
├── src/
│   ├── components/
│   │   ├── AlertCard.jsx (updated display)
│   │   └── AlertsPanel.jsx
│   ├── context/
│   │   └── WebSocketContext.jsx (Socket.IO)
│   └── data/
│       └── initialCameras.js (2 cameras only)
models/
├── crowd_yolo6/weights/best.pt
├── fight_yolo/weights/best.pt
├── weapon_yolo/weights/best.pt
└── weapon4/weights/best.pt
```

## 8. Installation & Setup

### Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start Flask server
python src/app.py
```

### Frontend Setup
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Start Detection
```bash
# Run detector
python src/detector/infer_detector.py
```

## 9. How It Works (Flow)

1. **Detection Loop** runs continuously on video feed
2. **Models Process** each frame:
   - Crowd model detects people
   - Knife model scans for knives
   - Weapon model scans for weapons
   - Fight classifier analyzes person crops
3. **Alert Triggered** when conditions met
4. **Three Actions Occur Simultaneously**:
   - Screenshot saved to `outputs/alerts/`
   - Alert logged to Excel file
   - HTTP POST to Flask `/api/alerts`
5. **Flask Receives Alert**:
   - Saves JSON to `alerts/` directory
   - Broadcasts via WebSocket to frontend
6. **Frontend Updates**:
   - Socket.IO receives `new_alert` event
   - Alert added to panel (max 20)
   - UI updates in real-time

## 10. Testing Checklist

- [ ] All 4 models load successfully
- [ ] Weapon detection triggers alert + Excel log
- [ ] Knife detection triggers alert + Excel log
- [ ] Fight detection triggers alert + Excel log
- [ ] 5+ people for 2+ minutes triggers crowd alert
- [ ] Excel file created with correct headers
- [ ] Flask server accepts alerts
- [ ] WebSocket broadcasts work
- [ ] Frontend receives real-time alerts
- [ ] Only 2 cameras display
- [ ] Alert panel shows detection type, time, camera name
- [ ] People count shown for crowd alerts
- [ ] Confidence shown for weapon/fight alerts

## 11. Key Features

✅ **Real-time Detection**: 4 AI models running simultaneously  
✅ **Smart Alerting**: Only alerts on actual events (weapon, fight, crowd persistence)  
✅ **Excel Logging**: Automatic spreadsheet with all alert details  
✅ **WebSocket Updates**: Live alerts pushed to frontend instantly  
✅ **Visual Feedback**: HUD display, color-coded boxes, blinking borders  
✅ **Audio Alerts**: Sound notifications for weapons/knives  
✅ **Configurable Thresholds**: Easy adjustment via config.yaml  
✅ **Dual Camera View**: Cleaner interface with 2 cameras  
✅ **Complete Alert Context**: Type, time, camera, confidence, people count  

## 12. Configuration

Edit `src/detector/config.yaml` to adjust:
- Video source path
- Model paths
- Detection confidence thresholds
- Group size threshold (currently 5)
- Group duration threshold (currently 120 seconds)
- Alert HTTP endpoint
- Output directories

## Notes

- Excel file grows with each alert - consider periodic archival
- Screenshots saved to `outputs/alerts/` - monitor disk space
- WebSocket connection auto-reconnects on failure
- Frontend shows last 20 alerts only (prevents memory issues)
- All times in ISO 8601 format for consistency
