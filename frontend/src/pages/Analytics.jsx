import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

const Analytics = () => {
  const navigate = useNavigate();
  const [detections, setDetections] = useState([]);
  const [stats, setStats] = useState({
    total: 0,
    weapon: 0,
    fight: 0,
    crowd: 0,
  });
  const [timelineData, setTimelineData] = useState([]);
  const [hourlyData, setHourlyData] = useState([]);

  useEffect(() => {
    fetchAnalyticsData();
    // Refresh every 10 seconds
    const interval = setInterval(fetchAnalyticsData, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchAnalyticsData = async () => {
    try {
      // Get today's date
      const today = new Date().toISOString().split('T')[0];
      
      // Fetch today's detections
      const response = await fetch(`http://localhost:5000/api/detections/${today}`);
      const data = await response.json();
      
      setDetections(data);
      
      // Calculate stats
      const weaponCount = data.filter(d => d.type === 'weapon').length;
      const fightCount = data.filter(d => d.type === 'fight').length;
      const crowdCount = data.filter(d => d.type === 'crowd').length;
      
      setStats({
        total: data.length,
        weapon: weaponCount,
        fight: fightCount,
        crowd: crowdCount,
      });
      
      // Process timeline data (last 2 hours)
      const twoHoursAgo = new Date(Date.now() - 2 * 60 * 60 * 1000);
      const recentData = data.filter(d => new Date(d.timestamp) >= twoHoursAgo);
      
      // Group by 10-minute intervals
      const timeline = {};
      recentData.forEach(detection => {
        const time = new Date(detection.timestamp);
        const minutes = Math.floor(time.getMinutes() / 10) * 10;
        const key = `${time.getHours()}:${minutes.toString().padStart(2, '0')}`;
        
        if (!timeline[key]) {
          timeline[key] = { time: key, weapon: 0, fight: 0, crowd: 0 };
        }
        timeline[key][detection.type]++;
      });
      
      setTimelineData(Object.values(timeline).sort((a, b) => a.time.localeCompare(b.time)));
      
      // Group by hour for daily view
      const hourly = {};
      data.forEach(detection => {
        const hour = new Date(detection.timestamp).getHours();
        const key = `${hour}:00`;
        
        if (!hourly[key]) {
          hourly[key] = { time: key, weapon: 0, fight: 0, crowd: 0 };
        }
        hourly[key][detection.type]++;
      });
      
      setHourlyData(Object.values(hourly).sort((a, b) => 
        parseInt(a.time) - parseInt(b.time)
      ));
      
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  const pieData = [
    { name: 'Weapon', value: stats.weapon, color: '#ef4444' },
    { name: 'Fight', value: stats.fight, color: '#f97316' },
    { name: 'Crowd', value: stats.crowd, color: '#eab308' },
  ];

  const recentAlerts = detections
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
    .slice(0, 10);

  return (
    <div className="min-h-screen bg-dark-bg p-6">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Analytics Dashboard</h1>
          <p className="text-gray-400">Real-time detection analytics and insights</p>
        </div>
        <button
          onClick={() => navigate('/')}
          className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Dashboard
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-700 rounded-lg p-6 shadow-lg">
          <div className="text-blue-100 text-sm mb-2">Total Alerts</div>
          <div className="text-4xl font-bold text-white">{stats.total}</div>
        </div>
        
        <div className="bg-gradient-to-br from-red-500 to-red-700 rounded-lg p-6 shadow-lg">
          <div className="text-red-100 text-sm mb-2">Weapon Detections</div>
          <div className="text-4xl font-bold text-white">{stats.weapon}</div>
        </div>
        
        <div className="bg-gradient-to-br from-orange-500 to-orange-700 rounded-lg p-6 shadow-lg">
          <div className="text-orange-100 text-sm mb-2">Fight Detections</div>
          <div className="text-4xl font-bold text-white">{stats.fight}</div>
        </div>
        
        <div className="bg-gradient-to-br from-yellow-500 to-yellow-700 rounded-lg p-6 shadow-lg">
          <div className="text-yellow-100 text-sm mb-2">Crowd Detections</div>
          <div className="text-4xl font-bold text-white">{stats.crowd}</div>
        </div>
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Detection Timeline (Last 2 Hours) */}
        <div className="bg-dark-surface border border-dark-border rounded-lg p-6">
          <h2 className="text-xl font-bold text-white mb-4">Detection Timeline (Last 2 Hours)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={timelineData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e2533" />
              <XAxis dataKey="time" stroke="#9ca3af" tick={{ fill: '#9ca3af' }} />
              <YAxis stroke="#9ca3af" tick={{ fill: '#9ca3af' }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#131824', border: '1px solid #1e2533', borderRadius: '8px' }}
                labelStyle={{ color: '#fff' }}
              />
              <Legend />
              <Line type="monotone" dataKey="weapon" stroke="#ef4444" strokeWidth={2} name="Weapon" />
              <Line type="monotone" dataKey="fight" stroke="#f97316" strokeWidth={2} name="Fight" />
              <Line type="monotone" dataKey="crowd" stroke="#eab308" strokeWidth={2} name="Crowd" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Detection Distribution */}
        <div className="bg-dark-surface border border-dark-border rounded-lg p-6">
          <h2 className="text-xl font-bold text-white mb-4">Detection Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ backgroundColor: '#131824', border: '1px solid #1e2533', borderRadius: '8px' }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Hourly Activity */}
        <div className="bg-dark-surface border border-dark-border rounded-lg p-6">
          <h2 className="text-xl font-bold text-white mb-4">Hourly Activity (Today)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={hourlyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e2533" />
              <XAxis dataKey="time" stroke="#9ca3af" tick={{ fill: '#9ca3af' }} />
              <YAxis stroke="#9ca3af" tick={{ fill: '#9ca3af' }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#131824', border: '1px solid #1e2533', borderRadius: '8px' }}
                labelStyle={{ color: '#fff' }}
              />
              <Legend />
              <Bar dataKey="weapon" fill="#ef4444" name="Weapon" />
              <Bar dataKey="fight" fill="#f97316" name="Fight" />
              <Bar dataKey="crowd" fill="#eab308" name="Crowd" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Recent Alerts Table */}
        <div className="bg-dark-surface border border-dark-border rounded-lg p-6">
          <h2 className="text-xl font-bold text-white mb-4">Recent Alerts</h2>
          <div className="overflow-auto max-h-[300px]">
            <table className="w-full text-sm">
              <thead className="bg-dark-bg sticky top-0">
                <tr className="text-gray-400 border-b border-dark-border">
                  <th className="py-2 px-3 text-left">Time</th>
                  <th className="py-2 px-3 text-left">Camera</th>
                  <th className="py-2 px-3 text-left">Type</th>
                  <th className="py-2 px-3 text-left">Confidence</th>
                </tr>
              </thead>
              <tbody>
                {recentAlerts.map((alert, index) => (
                  <tr key={index} className="border-b border-dark-border hover:bg-dark-hover">
                    <td className="py-2 px-3 text-white">
                      {new Date(alert.timestamp).toLocaleTimeString()}
                    </td>
                    <td className="py-2 px-3 text-white">{alert.camera}</td>
                    <td className="py-2 px-3">
                      <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                        alert.type === 'weapon' ? 'bg-red-500/20 text-red-400' :
                        alert.type === 'fight' ? 'bg-orange-500/20 text-orange-400' :
                        'bg-yellow-500/20 text-yellow-400'
                      }`}>
                        {alert.type.toUpperCase()}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-white">
                      {alert.confidence > 0 ? `${(alert.confidence * 100).toFixed(1)}%` : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
