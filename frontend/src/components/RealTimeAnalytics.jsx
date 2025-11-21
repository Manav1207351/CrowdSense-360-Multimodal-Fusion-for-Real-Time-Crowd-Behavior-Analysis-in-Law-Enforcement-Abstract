import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

const RealTimeAnalytics = ({ socket }) => {
  const [filter, setFilter] = useState('all'); // all, weapon, fight, crowd
  const [dateFilter, setDateFilter] = useState(new Date().toISOString().split('T')[0]);
  const [graphData, setGraphData] = useState(() => {
    // Load graph data from localStorage on mount
    const saved = localStorage.getItem('crowdsense_graph_data');
    return saved ? JSON.parse(saved) : [];
  });
  const [liveMode, setLiveMode] = useState(true);

  // Save graph data to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('crowdsense_graph_data', JSON.stringify(graphData));
  }, [graphData]);

  // Fetch historical data when date changes
  useEffect(() => {
    if (!liveMode) {
      fetchHistoricalData(dateFilter);
    }
  }, [dateFilter, filter, liveMode]);

  // Listen for real-time detections via WebSocket
  useEffect(() => {
    if (!socket || !liveMode) return;

    const handleNewAlert = (alertData) => {
      const timestamp = new Date(alertData.timestamp).toLocaleTimeString();
      
      // Check if alert matches filter
      if (filter !== 'all' && alertData.type !== filter) return;
      
      setGraphData(prev => {
        const newData = [...prev];
        const existingIndex = newData.findIndex(d => d.time === timestamp);
        
        if (existingIndex >= 0) {
          // Update existing entry
          newData[existingIndex] = {
            ...newData[existingIndex],
            [alertData.type]: (newData[existingIndex][alertData.type] || 0) + 1,
            total: (newData[existingIndex].total || 0) + 1
          };
        } else {
          // Add new entry
          newData.push({
            time: timestamp,
            weapon: alertData.type === 'weapon' ? 1 : 0,
            fight: alertData.type === 'fight' ? 1 : 0,
            crowd: alertData.type === 'crowd' ? 1 : 0,
            total: 1
          });
        }
        
        // Keep all data points for persistence (no limit)
        return newData;
      });
    };

    socket.on('new_alert', handleNewAlert);
    
    return () => socket.off('new_alert', handleNewAlert);
  }, [socket, filter, liveMode]);

  const fetchHistoricalData = async (date) => {
    try {
      const url = filter === 'all' 
        ? `http://localhost:5000/api/detections/${date}`
        : `http://localhost:5000/api/detections/${date}?type=${filter}`;
      
      const response = await fetch(url);
      const data = await response.json();
      
      // Group by hour
      const hourlyData = {};
      data.forEach(detection => {
        const hour = new Date(detection.timestamp).getHours();
        const timeLabel = `${hour}:00`;
        
        if (!hourlyData[timeLabel]) {
          hourlyData[timeLabel] = { time: timeLabel, weapon: 0, fight: 0, crowd: 0, total: 0 };
        }
        
        hourlyData[timeLabel][detection.type] = (hourlyData[timeLabel][detection.type] || 0) + 1;
        hourlyData[timeLabel].total += 1;
      });
      
      setGraphData(Object.values(hourlyData).sort((a, b) => 
        parseInt(a.time) - parseInt(b.time)
      ));
    } catch (error) {
      console.error('Error fetching historical data:', error);
    }
  };

  return (
    <div className="bg-dark-surface border border-dark-border rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <h3 className="text-lg font-bold text-white">
            {liveMode ? 'Real-Time Analytics' : `Analytics - ${dateFilter}`}
          </h3>
          <span className="text-xs text-gray-400">
            ({graphData.length} data points)
          </span>
        </div>
        
        <div className="flex gap-3 items-center">
          {/* Clear Data Button (only in live mode) */}
          {liveMode && graphData.length > 0 && (
            <button
              onClick={() => {
                if (window.confirm('Clear all graph data? This cannot be undone.')) {
                  setGraphData([]);
                  localStorage.removeItem('crowdsense_graph_data');
                }
              }}
              className="px-3 py-1 rounded text-xs font-medium transition-colors bg-red-600 text-white hover:bg-red-700"
            >
              🗑️ Clear
            </button>
          )}
          
          {/* Live/Historical Toggle */}
          <button
            onClick={() => setLiveMode(!liveMode)}
            className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
              liveMode
                ? 'bg-green-600 text-white'
                : 'bg-gray-600 text-white'
            }`}
          >
            {liveMode ? '🔴 LIVE' : '📊 Historical'}
          </button>
          
          {/* Date Picker (only in historical mode) */}
          {!liveMode && (
            <input
              type="date"
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
              className="px-3 py-1 rounded text-xs bg-dark-bg border border-dark-border text-white"
            />
          )}
          
          {/* Filter Buttons */}
          <div className="flex gap-2">
            {['all', 'weapon', 'fight', 'crowd'].map((type) => (
              <button
                key={type}
                onClick={() => setFilter(type)}
                className={`px-3 py-1 rounded text-xs font-medium transition-colors capitalize ${
                  filter === type
                    ? 'bg-blue-600 text-white'
                    : 'bg-dark-hover text-gray-400 hover:bg-dark-border'
                }`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={graphData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e2533" />
          <XAxis
            dataKey="time"
            stroke="#6b7280"
            tick={{ fill: '#9ca3af', fontSize: 12 }}
          />
          <YAxis
            stroke="#6b7280"
            tick={{ fill: '#9ca3af', fontSize: 12 }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#131824',
              border: '1px solid #1e2533',
              borderRadius: '8px',
            }}
            labelStyle={{ color: '#fff' }}
          />
          <Legend />
          
          {(filter === 'all' || filter === 'weapon') && (
            <Line type="monotone" dataKey="weapon" stroke="#ef4444" strokeWidth={2} name="Weapon" />
          )}
          {(filter === 'all' || filter === 'fight') && (
            <Line type="monotone" dataKey="fight" stroke="#f97316" strokeWidth={2} name="Fight" />
          )}
          {(filter === 'all' || filter === 'crowd') && (
            <Line type="monotone" dataKey="crowd" stroke="#eab308" strokeWidth={2} name="Crowd" />
          )}
          {filter === 'all' && (
            <Line type="monotone" dataKey="total" stroke="#3b82f6" strokeWidth={2} name="Total" />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default RealTimeAnalytics;
