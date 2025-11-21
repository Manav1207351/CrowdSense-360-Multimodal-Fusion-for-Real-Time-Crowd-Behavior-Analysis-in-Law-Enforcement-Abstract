import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import Sidebar from '../components/Sidebar';
import CameraTile from '../components/CameraTile';
import RealTimeAnalytics from '../components/RealTimeAnalytics';
import AlertsPanel from '../components/AlertsPanel';
import { initialCameras } from '../data/initialCameras';
import io from 'socket.io-client';

const Dashboard = () => {
  const [cameras, setCameras] = useState(initialCameras);
  const [alerts, setAlerts] = useState(() => {
    // Load alerts from localStorage on mount
    const saved = localStorage.getItem('crowdsense_alerts');
    return saved ? JSON.parse(saved) : [];
  });
  const [selectedCamera, setSelectedCamera] = useState('Cam-1');
  const [socket, setSocket] = useState(null);

  // Save alerts to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('crowdsense_alerts', JSON.stringify(alerts));
  }, [alerts]);

  // WebSocket connection for real-time alerts
  useEffect(() => {
    const newSocket = io('http://localhost:5000');
    setSocket(newSocket);
    
    newSocket.on('connect', () => {
      console.log('✅ Connected to WebSocket');
    });

    newSocket.on('new_alert', (alertData) => {
      console.log('📡 Received alert:', alertData);
      
      const newAlert = {
        id: Date.now() + Math.random(),
        alertType: alertData.type,
        severity: alertData.severity || (alertData.type === 'weapon' ? 'high' : 'medium'),
        evidence: alertData.type === 'weapon' ? ['object detection'] : ['crowd analysis'],
        cameraId: alertData.camera,
        timestamp: alertData.timestamp || new Date().toISOString(),
        confidence: alertData.confidence,
        count: alertData.count,
        duration: alertData.duration,
        message: alertData.message
      };
      
      setAlerts((prev) => [newAlert, ...prev].slice(0, 50)); // Keep last 50 alerts
    });

    return () => newSocket.disconnect();
  }, []);

  const handleCameraStatusChange = (cameraId, status, resetStats = false) => {
    console.log('handleCameraStatusChange called:', { cameraId, status, resetStats });
    
    setCameras((prev) =>
      prev.map((cam) =>
        cam.id === cameraId 
          ? { 
              ...cam, 
              status,
              ...(resetStats && { count: 0, flow: 0 })
            } 
          : cam
      )
    );

    // Don't clear alerts when stopping - keep them persistent
  };

  const handleVideoUpload = (cameraId, result) => {
    // Update camera count and flow from backend response
    if (result.count !== undefined || result.flow !== undefined) {
      setCameras((prev) =>
        prev.map((cam) =>
          cam.id === cameraId
            ? { 
                ...cam, 
                count: result.count || cam.count,
                flow: result.flow || cam.flow 
              }
            : cam
        )
      );
    }

    // Create alerts from detection results
    const newAlerts = [];
    
    if (result.crowd) {
      newAlerts.push({
        id: Date.now() + Math.random(),
        alertType: 'crowd',
        severity: result.crowd_severity || 'med',
        evidence: ['density', 'visual'],
        cameraId: cameraId,
        timestamp: new Date().toISOString(),
      });
    }

    if (result.fight) {
      newAlerts.push({
        id: Date.now() + Math.random() + 1,
        alertType: 'fight',
        severity: 'high',
        evidence: ['motion', 'visual'],
        cameraId: cameraId,
        timestamp: new Date().toISOString(),
      });
    }

    if (result.weapon) {
      newAlerts.push({
        id: Date.now() + Math.random() + 2,
        alertType: 'weapon',
        severity: 'high',
        evidence: ['object detection', 'visual'],
        cameraId: cameraId,
        timestamp: new Date().toISOString(),
      });
    }

    // Add new alerts to the list
    if (newAlerts.length > 0) {
      setAlerts((prev) => [...newAlerts, ...prev].slice(0, 20));
    }
  };

  return (
    <div className="flex flex-col h-screen bg-dark-bg">
      <Header connected={true} />
      
      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          selectedCamera={selectedCamera}
          onSelectCamera={setSelectedCamera}
          cameras={cameras}
        />

        <main className="flex-1 overflow-y-auto p-6">
          {/* Camera Grid - 2x2 */}
          <div className="grid grid-cols-2 gap-6 mb-6">
            {cameras.map((camera) => (
              <CameraTile 
                key={camera.id} 
                camera={camera}
                onVideoUpload={handleVideoUpload}
                onStatusChange={handleCameraStatusChange}
              />
            ))}
          </div>

          {/* Real-Time Analytics */}
          <RealTimeAnalytics socket={socket} />
        </main>

        <AlertsPanel alerts={alerts} />
      </div>
    </div>
  );
};

export default Dashboard;
