import React from 'react';
import { mapSeverityColor, mapAlertType } from '../utils/mapSeverityColor';
import { formatTime } from '../utils/formatTime';

const AlertCard = ({ alert }) => {
  const colors = mapSeverityColor(alert.severity);
  const { label, icon } = mapAlertType(alert.alertType);

  // Format camera name
  const cameraName = alert.cameraId || 'Unknown Camera';
  
  // Format timestamp to readable format
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  return (
    <div
      className={`${colors.bg} ${colors.border} border rounded-lg p-4 transition-all hover:scale-[1.02]`}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-xl">{icon}</span>
          <h4 className={`font-semibold ${colors.text}`}>{label}</h4>
        </div>
        <span
          className={`${colors.badge} ${colors.badgeText} px-2 py-1 rounded text-xs font-bold uppercase`}
        >
          {alert.severity}
        </span>
      </div>

      <div className="space-y-2">
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <svg
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
            />
          </svg>
          <span>{cameraName}</span>
        </div>

        {/* Show custom message if available */}
        {alert.message && (
          <div className="text-sm text-gray-300 bg-dark-bg/50 p-2 rounded">
            {alert.message}
          </div>
        )}

        {/* Show people count for crowd alerts */}
        {alert.count > 0 && (
          <div className="text-sm text-gray-300">
            👥 People: {alert.count}
          </div>
        )}
        
        {/* Show duration for group alerts */}
        {alert.duration > 0 && (
          <div className="text-sm text-yellow-400">
            ⏱️ Duration: {alert.duration}s
          </div>
        )}

        {/* Show confidence for weapon alerts */}
        {alert.confidence && (
          <div className="text-sm text-gray-300">
            📊 Confidence: {(alert.confidence * 100).toFixed(1)}%
          </div>
        )}

        <div className="flex items-center gap-2 flex-wrap">
          {alert.evidence && alert.evidence.map((tag, idx) => (
            <span
              key={idx}
              className="bg-dark-surface border border-dark-border px-2 py-1 rounded text-xs text-gray-300"
            >
              {tag}
            </span>
          ))}
        </div>

        <div className="text-xs text-gray-400 mt-2 flex items-center gap-1">
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {formatTimestamp(alert.timestamp)}
        </div>
      </div>
    </div>
  );
};

export default AlertCard;
