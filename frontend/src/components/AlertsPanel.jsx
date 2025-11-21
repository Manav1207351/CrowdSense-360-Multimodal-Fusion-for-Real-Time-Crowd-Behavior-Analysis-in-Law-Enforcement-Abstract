import React, { useState } from 'react';
import AlertCard from './AlertCard';

const AlertsPanel = ({ alerts = [] }) => {
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [typeFilter, setTypeFilter] = useState('all');
  const [dateFilter, setDateFilter] = useState('');

  const filteredAlerts = alerts.filter((alert) => {
    // Severity filter
    if (severityFilter !== 'ALL' && alert.severity.toUpperCase() !== severityFilter) {
      return false;
    }
    
    // Type filter
    if (typeFilter !== 'all' && alert.alertType !== typeFilter) {
      return false;
    }
    
    // Date filter
    if (dateFilter) {
      const alertDate = new Date(alert.timestamp).toISOString().split('T')[0];
      if (alertDate !== dateFilter) {
        return false;
      }
    }
    
    return true;
  });

  return (
    <aside className="w-96 bg-dark-surface border-l border-dark-border p-4 overflow-y-auto">
      <div className="mb-4">
        <h2 className="text-lg font-bold text-white mb-3">Live Alerts</h2>
        
        {/* Date Filter */}
        <div className="mb-3">
          <label className="text-xs text-gray-400 mb-1 block">Filter by Date</label>
          <input
            type="date"
            value={dateFilter}
            onChange={(e) => setDateFilter(e.target.value)}
            className="w-full px-3 py-1.5 rounded text-xs bg-dark-bg border border-dark-border text-white"
          />
          {dateFilter && (
            <button
              onClick={() => setDateFilter('')}
              className="text-xs text-blue-500 hover:text-blue-400 mt-1"
            >
              Clear date filter
            </button>
          )}
        </div>
        
        {/* Type Filter */}
        <div className="mb-3">
          <label className="text-xs text-gray-400 mb-1 block">Detection Type</label>
          <div className="flex gap-2">
            {['all', 'weapon', 'fight', 'crowd'].map((type) => (
              <button
                key={type}
                onClick={() => setTypeFilter(type)}
                className={`px-3 py-1 rounded text-xs font-medium transition-colors capitalize flex-1 ${
                  typeFilter === type
                    ? 'bg-blue-600 text-white'
                    : 'bg-dark-hover text-gray-400 hover:bg-dark-border'
                }`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>
        
        {/* Severity Filter */}
        <div className="mb-3">
          <label className="text-xs text-gray-400 mb-1 block">Severity</label>
          <div className="flex gap-2">
            {['ALL', 'HIGH', 'MED', 'LOW'].map((level) => (
              <button
                key={level}
                onClick={() => setSeverityFilter(level)}
                className={`px-3 py-1 rounded text-xs font-medium transition-colors flex-1 ${
                  severityFilter === level
                    ? 'bg-blue-600 text-white'
                    : 'bg-dark-hover text-gray-400 hover:bg-dark-border'
                }`}
              >
                {level}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Alerts List */}
      <div className="space-y-3">
        {filteredAlerts.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <svg
              className="w-16 h-16 mx-auto mb-2 opacity-50"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
              />
            </svg>
            <p className="text-sm">No alerts match filters</p>
          </div>
        ) : (
          filteredAlerts.map((alert) => (
            <AlertCard key={alert.id} alert={alert} />
          ))
        )}
      </div>
    </aside>
  );
};

export default AlertsPanel;
