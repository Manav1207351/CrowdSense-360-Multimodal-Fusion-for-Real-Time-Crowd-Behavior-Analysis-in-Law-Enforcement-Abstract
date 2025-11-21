# 🚀 CrowdSense 360 – Live Operations Dashboard

A **production-ready**, **real-time** frontend for Crowd/Fight/Weapon Detection using React, Tailwind CSS, and WebSockets.

---

## ✨ Features

✅ **Real-time WebSocket Updates** - No timers, no polling. Updates happen ONLY when backend sends data.  
✅ **Dark Theme Dashboard** - Modern, professional UI matching your design.  
✅ **4 Camera Tiles** - 2x2 grid showing live count and flow data.  
✅ **Event Timeline Chart** - Displays last 15 minutes of events using Recharts.  
✅ **Live Alerts Panel** - Shows crowd/fight/weapon detections with severity filtering.  
✅ **Camera Sidebar** - Lists all cameras with online/offline status.  
✅ **Live Clock** - Real-time date and time display.

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Sidebar.jsx              # Camera list sidebar
│   │   ├── CameraTile.jsx           # Individual camera tile with count/flow
│   │   ├── EventTimeline.jsx        # Bar chart for event timeline
│   │   ├── AlertsPanel.jsx          # Live alerts with filtering
│   │   ├── AlertCard.jsx            # Individual alert display
│   │   ├── Header.jsx               # Top header with title and clock
│   │   ├── StatusBadge.jsx          # Online/Offline indicator
│   │   └── RealtimeClock.jsx        # Live clock component
│   │
│   ├── context/
│   │   └── WebSocketContext.jsx     # WebSocket connection handler
│   │
│   ├── hooks/
│   │   └── useWebSocket.js          # Custom hook for WebSocket data
│   │
│   ├── data/
│   │   ├── initialCameras.js        # Initial camera data
│   │   ├── initialTimeline.js       # Initial timeline data
│   │   └── initialAlerts.js         # Initial alerts data
│   │
│   ├── utils/
│   │   ├── formatTime.js            # Time formatting utilities
│   │   └── mapSeverityColor.js      # Severity color mapping
│   │
│   ├── pages/
│   │   └── Dashboard.jsx            # Main dashboard page
│   │
│   ├── App.jsx                      # App entry with WebSocket provider
│   ├── index.jsx                    # React DOM root
│   └── index.css                    # Global styles with Tailwind
│
├── package.json                     # Dependencies and scripts
├── vite.config.js                   # Vite configuration
├── tailwind.config.js               # Tailwind configuration
├── postcss.config.js                # PostCSS configuration
└── index.html                       # HTML entry point
```

---

## 🛠️ Installation & Setup

### Prerequisites

- **Node.js** (v18 or higher)
- **npm** or **yarn**

### Step 1: Install Dependencies

```powershell
cd a:\src\frontend
npm install
```

### Step 2: Start the Development Server

```powershell
npm run dev
```

The dashboard will open automatically at `http://localhost:3000`

---

## 📡 WebSocket Integration

### Backend WebSocket URL

```javascript
ws://localhost:8080
```

### Message Types

The frontend listens for these message types from the backend:

#### 1. Camera Status Update
```json
{
  "type": "camera_status",
  "cameraId": "Cam-1",
  "status": "online"
}
```

#### 2. Frame Analysis (Count & Flow)
```json
{
  "type": "frame_analysis",
  "cameraId": "Cam-2",
  "count": 35,
  "flow": 12
}
```

#### 3. Detection Alert
```json
{
  "type": "detection_alert",
  "alertType": "crowd",
  "severity": "high",
  "evidence": ["density", "visual"],
  "cameraId": "Cam-3",
  "timestamp": "2025-11-17T14:20:00Z"
}
```

#### 4. Event Timeline Update
```json
{
  "type": "event_timeline_update",
  "data": [
    { "minute": -14, "events": 4 },
    { "minute": -13, "events": 7 },
    ...
    { "minute": 0, "events": 6 }
  ]
}
```

---

## 🎨 UI Components Breakdown

### Header
- Title: "CrowdSense 360 – Live Operations"
- Real-time clock (HH:MM:SS)
- WebSocket connection indicator

### Sidebar
- Lists all cameras
- Shows offline badges
- Camera selection (for future features)

### Camera Tiles (2x2 Grid)
- Camera name and location
- Online/Offline status badge
- Upload Video button
- Live Camera button
- Count and Flow stats

### Event Timeline
- Bar chart showing last 15 minutes of events
- Updates in real-time when backend sends data

### Alerts Panel
- Filter buttons: ALL, HIGH, MED, LOW
- Live alerts with severity color coding
- Evidence tags
- Camera source
- Timestamp ("2m ago" format)

---

## 🔄 Real-time Behavior

**IMPORTANT:** This system does NOT use timers or intervals for data updates.

All updates happen through WebSocket messages:

1. **WebSocketContext** establishes connection on app load
2. **Backend sends messages** when detections occur
3. **Frontend updates instantly** via React state
4. **No polling, no fake data, no timers**

The only timer used is for the clock display (updates every second).

---

## 🚀 Build for Production

```powershell
npm run build
```

This creates an optimized build in the `dist/` folder.

### Preview Production Build

```powershell
npm run preview
```

---

## 🧪 Testing with Mock Backend

If you don't have a WebSocket backend yet, you can test the frontend by creating a simple mock server:

### Create `mock-server.js` in the frontend folder:

```javascript
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', (ws) => {
  console.log('✅ Client connected');

  // Send camera status every 5 seconds
  setInterval(() => {
    ws.send(JSON.stringify({
      type: 'camera_status',
      cameraId: 'Cam-1',
      status: 'online'
    }));
  }, 5000);

  // Send frame analysis every 3 seconds
  setInterval(() => {
    ws.send(JSON.stringify({
      type: 'frame_analysis',
      cameraId: 'Cam-2',
      count: Math.floor(Math.random() * 50),
      flow: Math.floor(Math.random() * 20)
    }));
  }, 3000);

  // Send detection alert every 10 seconds
  setInterval(() => {
    ws.send(JSON.stringify({
      type: 'detection_alert',
      alertType: ['crowd', 'fight', 'weapon'][Math.floor(Math.random() * 3)],
      severity: ['high', 'med', 'low'][Math.floor(Math.random() * 3)],
      evidence: ['density', 'visual'],
      cameraId: 'Cam-3',
      timestamp: new Date().toISOString()
    }));
  }, 10000);
});

console.log('🚀 Mock WebSocket server running on ws://localhost:8080');
```

### Run mock server:

```powershell
npm install ws
node mock-server.js
```

---

## 📦 Dependencies

### Core
- `react` - UI library
- `react-dom` - React rendering
- `recharts` - Charts for event timeline
- `lucide-react` - Icons (optional, not used but available)

### Dev Tools
- `vite` - Build tool and dev server
- `tailwindcss` - Utility-first CSS framework
- `autoprefixer` - CSS vendor prefixing
- `postcss` - CSS processing

---

## 🎯 Key Features Summary

| Feature | Status |
|---------|--------|
| Real-time WebSocket connection | ✅ |
| Camera status updates | ✅ |
| Frame analysis (count/flow) | ✅ |
| Detection alerts | ✅ |
| Event timeline chart | ✅ |
| Severity filtering | ✅ |
| Dark theme UI | ✅ |
| Responsive layout | ✅ |
| Live clock | ✅ |
| Clean folder structure | ✅ |

---

## 🐛 Troubleshooting

### WebSocket won't connect
- Ensure backend is running on `ws://localhost:8080`
- Check browser console for connection errors
- Verify firewall settings

### Alerts not showing
- Check that backend is sending `detection_alert` messages
- Verify message format matches expected structure
- Open browser DevTools → Network → WS to inspect messages

### Timeline not updating
- Ensure backend sends `event_timeline_update` messages
- Check data format: must be array of `{ minute, events }`

---

## 📄 License

MIT License - Free to use for any purpose.

---

## 👨‍💻 Support

For issues or questions, check the browser console for errors and verify WebSocket messages in DevTools.

---

**Built with ❤️ using React + Tailwind CSS + WebSockets**
