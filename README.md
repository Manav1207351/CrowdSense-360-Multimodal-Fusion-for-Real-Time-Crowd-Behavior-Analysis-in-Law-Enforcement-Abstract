# CrowdSense-360: Multimodal Fusion for Real-Time Crowd Behavior Analysis

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/React-18.0+-61DAFB.svg)](https://reactjs.org/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-purple.svg)](https://github.com/ultralytics/ultralytics)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

## 📋 Overview

CrowdSense-360 is an advanced real-time crowd behavior analysis system designed for law enforcement and security operations. It leverages state-of-the-art deep learning models to detect and analyze crowd dynamics, fight incidents, and suspicious activities through live camera feeds and uploaded video footage.

### Key Features

- 🎥 **Real-Time Video Analysis**: Process live camera feeds and uploaded videos with YOLO-based detection models
- 👥 **Crowd Detection**: Monitor crowd formation, density, and group behaviors with configurable thresholds
- 🥊 **Fight Detection**: Identify violent incidents and altercations using specialized behavioral models
- 📊 **Live Analytics Dashboard**: Interactive web interface with real-time charts and statistics
- 🔔 **Intelligent Alerting**: WebSocket-based instant notifications for critical events
- 📸 **Screenshot Capture**: Automatic evidence collection with timestamped images
- 📈 **Excel Reporting**: Automated detection logs with embedded screenshots and color-coded severity
- 🕒 **Historical Analysis**: Date-based filtering and trend analysis capabilities
- 💾 **Persistent Storage**: JSON-based detection logs with localStorage frontend caching

## 🏗️ System Architecture

### Backend Stack
- **Framework**: Flask + Flask-SocketIO
- **Computer Vision**: OpenCV (cv2) with CAP_DSHOW support
- **Deep Learning**: Ultralytics YOLOv8
- **Data Export**: openpyxl + PIL for Excel generation
- **Real-time Communication**: Socket.IO

### Frontend Stack
- **Framework**: React 18 with JSX
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Routing**: React Router DOM
- **Real-time**: Socket.IO Client

### Detection Models
1. **Crowd Detection Model**
   - Path: `models/crowd_yolo6/weights/best.pt`
   - Confidence Threshold: 0.15
   - Purpose: Group formation and crowd density analysis

2. **Fight Detection Model**
   - Path: `models/fight_yolo/weights/best.pt`
   - Confidence Threshold: 0.25
   - Purpose: Violent behavior and altercation detection
   - Sustained Detection: 3-second minimum

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Node.js 16+ and npm
- Git
- Windows OS (optimized for Windows with CAP_DSHOW)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Manav1207351/CrowdSense-360-Multimodal-Fusion-for-Real-Time-Crowd-Behavior-Analysis-in-Law-Enforcement-Abstract.git
   cd CrowdSense-360
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Verify model files**
   Ensure the following model files exist:
   - `models/crowd_yolo6/weights/best.pt`
   - `models/fight_yolo/weights/best.pt`

### Running the Application

#### Option 1: Run Everything (Recommended)
```bash
.\start-all.ps1
```

#### Option 2: Run Services Separately

**Backend Server:**
```bash
.\start-backend.ps1
# or manually:
cd src
python app.py
```

**Frontend Development Server:**
```bash
.\start-frontend.ps1
# or manually:
cd frontend
npm run dev
```

### Access the Application

- **Frontend Dashboard**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **Analytics Page**: http://localhost:5173/analytics

## 📖 Usage Guide

### 1. Upload Video for Analysis

1. Navigate to the Dashboard
2. Select a camera tile
3. Click "Upload Video" and choose your video file
4. Detection results appear in real-time with overlays

### 2. Start Live Camera Feed

1. Click "Start Live Camera" on any camera tile
2. Enter camera index (default: 0 for primary webcam)
3. Live detection begins immediately
4. View detections on the video feed with bounding boxes

### 3. View Analytics

1. Click the "Analytics" button in the header
2. View real-time charts:
   - Line chart: Detection trends over time
   - Pie chart: Distribution by detection type
   - Bar chart: Hourly detection counts
3. Filter by detection type (All, Fight, Crowd)
4. Select specific dates for historical analysis

### 4. Monitor Alerts

- Real-time alerts appear in the AlertsPanel
- Filter by severity and detection type
- Each alert shows timestamp, camera, and confidence level
- Color-coded by severity (critical/warning)

### 5. Export Detection Data

Detection data is automatically saved to:
- **Excel**: `detection_alerts.xlsx` (with screenshots)
- **JSON Logs**: `detections/YYYY-MM-DD.json`
- **Screenshots**: `screenshots/` directory

## 🔧 Configuration

### Detection Thresholds

Edit `src/detector/config.yaml`:

```yaml
models:
  crowd:
    path: "models/crowd_yolo6/weights/best.pt"
  fight:
    path: "models/fight_yolo/weights/best.pt"

thresholds:
  detection_conf: 0.25
  fight_conf: 0.25
  crowd_threshold: 5      # Minimum persons to trigger crowd alert
  group_duration: 3       # Seconds before group alert
```

### Camera Configuration

Modify camera settings in `src/app.py`:

```python
VIDEO_SESSIONS = {}
CAMERA_CONFIGS = {
    'camera_0': {'index': 0, 'name': 'Front Entrance'},
    'camera_1': {'index': 1, 'name': 'Main Hall'},
    # Add more cameras as needed
}
```

## 📊 API Endpoints

### Detection & Streaming

- `POST /api/detect` - Upload video for analysis
- `GET /api/video_feed/<camera_id>` - MJPEG stream with detections
- `POST /api/start_live_camera/<camera_id>` - Start live camera session

### Data Retrieval

- `GET /api/alerts` - Fetch all alerts
- `GET /api/detections/<date>` - Get detections for specific date (YYYY-MM-DD)
- `GET /api/detections/range?start=<date>&end=<date>` - Date range query

### Real-time Updates

- WebSocket event: `new_alert` - Emitted when new detection occurs

## 🧪 Testing

### Test Model Accuracy

Run the practical accuracy checker:

```bash
python check_model_accuracy.py
```

This will test both models on sample videos and output results to `model_accuracy_test_results.json`.

### Integration Testing

```bash
python test_integration.py
```

## 📁 Project Structure

```
CrowdSense-360/
├── src/
│   ├── app.py                 # Main Flask application
│   ├── detector/              # Detection modules
│   │   ├── config.yaml        # Model configuration
│   │   ├── behaviour_logic.py # Behavior analysis
│   │   ├── fight_classifier.py
│   │   ├── group_detector.py
│   │   └── yolo_loader.py
│   ├── trackers/              # Object tracking
│   ├── utils/                 # Utility functions
│   ├── static/                # CSS/JS assets
│   └── templates/             # HTML templates
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── context/           # WebSocket context
│   │   └── utils/             # Helper functions
│   ├── index.html
│   └── package.json
├── models/                    # YOLO model weights
│   ├── crowd_yolo6/
│   └── fight_yolo/
├── detections/                # JSON detection logs
├── screenshots/               # Captured images
├── alerts/                    # Alert data
├── requirements.txt           # Python dependencies
├── check_model_accuracy.py    # Model testing script
└── README.md
```

## 🎯 Detection Logic

### Crowd Detection
1. YOLO model predicts person bounding boxes (conf > 0.15)
2. Counts total persons in frame
3. If count ≥ 5: starts group timer
4. After 3 seconds sustained: triggers crowd alert
5. Logs to JSON, Excel, and emits WebSocket event

### Fight Detection
1. YOLO model predicts fight behavior (conf > 0.25)
2. Requires sustained detection over 3 seconds
3. Prevents false positives from brief movements
4. High-priority alert with critical severity
5. Automatic screenshot capture for evidence

## 🔐 Security Considerations

- All file uploads are validated for video formats
- Model confidence thresholds prevent false alerts
- Sustained detection logic reduces noise
- Screenshot storage is timestamped and indexed
- Excel exports are color-coded by severity

## 🛠️ Troubleshooting

### Camera not detected
- Verify camera index in live camera setup
- Ensure CAP_DSHOW backend is available (Windows)
- Check camera permissions in system settings

### Models not loading
- Confirm model files exist at specified paths
- Verify sufficient disk space and memory
- Check Python ultralytics package installation

### Frontend not updating
- Clear browser localStorage: `localStorage.clear()`
- Verify WebSocket connection in browser console
- Check backend is running on port 5000

### Poor detection accuracy
- Adjust confidence thresholds in config.yaml
- Ensure proper lighting in camera view
- Test with sample videos using `check_model_accuracy.py`

## 📝 Future Enhancements

- [ ] Multi-camera synchronization
- [ ] Advanced analytics with ML insights
- [ ] Mobile application support
- [ ] Cloud deployment option
- [ ] Advanced threat classification
- [ ] Integration with access control systems
- [ ] Facial recognition capabilities
- [ ] License plate recognition (OCR module exists in `src/ocr/`)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Manav** - Initial work and development

## 🙏 Acknowledgments

- Ultralytics for YOLOv8 framework
- Flask and React communities
- OpenCV contributors
- All open-source libraries used in this project

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: [Your contact information]

---

**Note**: This system is designed for law enforcement and security professionals. Ensure compliance with local privacy and surveillance regulations before deployment.