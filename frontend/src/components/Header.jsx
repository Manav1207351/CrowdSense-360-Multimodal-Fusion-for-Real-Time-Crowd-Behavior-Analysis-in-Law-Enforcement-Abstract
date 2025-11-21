import React from 'react';
import { useNavigate } from 'react-router-dom';
import RealtimeClock from './RealtimeClock';

const Header = ({ connected = true }) => {
  const navigate = useNavigate();
  
  const handleOpenAnalytics = () => {
    navigate('/analytics');
  };

  return (
    <header className="bg-dark-surface border-b border-dark-border px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-bold text-white">
            CrowdSense 360 – Live Operations
          </h1>
          <div className="flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${
                connected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
              }`}
            />
            <span className="text-xs text-gray-400">
              {connected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          {/* Analytics Button */}
          <button
            onClick={handleOpenAnalytics}
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 shadow-lg"
          >
            <svg 
              className="w-5 h-5" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" 
              />
            </svg>
            Analytics
          </button>
          
          <RealtimeClock />
        </div>
      </div>
    </header>
  );
};

export default Header;
