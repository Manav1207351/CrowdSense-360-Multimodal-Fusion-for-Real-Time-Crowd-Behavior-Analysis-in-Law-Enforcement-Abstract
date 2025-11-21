import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { io } from 'socket.io-client';
import { initialCameras } from '../data/initialCameras';
import { initialTimeline } from '../data/initialTimeline';
import { initialAlerts } from '../data/initialAlerts';

const WebSocketContext = createContext(null);

export const useWebSocketContext = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocketContext must be used within WebSocketProvider');
  }
  return context;
};

export const WebSocketProvider = ({ children }) => {
  const [ws, setWs] = useState(null);
  const [connected, setConnected] = useState(false);
  const [cameras, setCameras] = useState(initialCameras);
  const [timeline, setTimeline] = useState(initialTimeline);
  const [alerts, setAlerts] = useState(initialAlerts);

  // Handle incoming WebSocket messages
  const handleMessage = useCallback((event) => {
    try {
      const message = JSON.parse(event.data);
      
      switch (message.type) {
        case 'camera_status':
          handleCameraStatus(message);
          break;
        case 'frame_analysis':
          handleFrameAnalysis(message);
          break;
        case 'detection_alert':
          handleDetectionAlert(message);
          break;
        case 'event_timeline_update':
          handleTimelineUpdate(message);
          break;
        default:
          console.log('Unknown message type:', message.type);
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }, []);

  // Update camera status (online/offline)
  const handleCameraStatus = (message) => {
    setCameras((prev) =>
      prev.map((cam) =>
        cam.id === message.cameraId
          ? { ...cam, status: message.status }
          : cam
      )
    );
  };

  // Update camera count and flow
  const handleFrameAnalysis = (message) => {
    setCameras((prev) =>
      prev.map((cam) =>
        cam.id === message.cameraId
          ? { ...cam, count: message.count, flow: message.flow }
          : cam
      )
    );
  };

  // Add new detection alert
  const handleDetectionAlert = (message) => {
    const newAlert = {
      id: Date.now() + Math.random(), // Unique ID
      alertType: message.alertType,
      severity: message.severity,
      evidence: message.evidence,
      cameraId: message.cameraId,
      timestamp: message.timestamp,
    };

    setAlerts((prev) => {
      // Keep only last 20 alerts
      const updated = [newAlert, ...prev];
      return updated.slice(0, 20);
    });
  };

  // Update event timeline
  const handleTimelineUpdate = (message) => {
    if (message.data && Array.isArray(message.data)) {
      setTimeline(message.data.map(item => ({
        ...item,
        label: `${item.minute}m`
      })));
    }
  };

  // Initialize Socket.IO connection
  useEffect(() => {
    const socket = io('http://localhost:5000', {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 10
    });

    socket.on('connect', () => {
      console.log('✅ Socket.IO connected');
      setConnected(true);
    });

    socket.on('connection_status', (data) => {
      console.log('Connection status:', data);
    });

    socket.on('new_alert', (data) => {
      console.log('📡 Received alert:', data);
      
      // Map backend alert format to frontend format
      const alertType = data.type === 'crowd_group_complete' ? 'crowd' : data.type;
      const severity = data.type === 'weapon' || data.type === 'fight' ? 'high' : 'med';
      
      const newAlert = {
        id: Date.now() + Math.random(),
        alertType: alertType,
        severity: severity,
        evidence: data.type === 'crowd_group_complete' ? ['density', 'duration'] : ['visual', 'detection'],
        cameraId: data.camera || 'Camera-1',
        timestamp: data.time,
        peopleCount: data.people_count || 0,
        confidence: data.confidence || 0
      };

      setAlerts((prev) => [newAlert, ...prev].slice(0, 20));
    });

    socket.on('disconnect', () => {
      console.log('🔌 Socket.IO disconnected');
      setConnected(false);
    });

    socket.on('error', (error) => {
      console.error('❌ Socket.IO error:', error);
    });

    setWs(socket);

    // Cleanup on unmount
    return () => {
      socket.disconnect();
    };
  }, []);

  const value = {
    ws,
    connected,
    cameras,
    timeline,
    alerts,
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};
