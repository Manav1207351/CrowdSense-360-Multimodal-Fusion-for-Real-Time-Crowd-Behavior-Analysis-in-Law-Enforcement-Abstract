import React from 'react';

const StatusBadge = ({ status }) => {
  const isOnline = status === 'online';

  return (
    <div className="flex items-center gap-2">
      <div
        className={`w-2 h-2 rounded-full ${
          isOnline ? 'bg-green-500 animate-pulse' : 'bg-red-500'
        }`}
      />
      <span
        className={`text-xs font-medium ${
          isOnline ? 'text-green-400' : 'text-red-400'
        }`}
      >
        {isOnline ? 'Online' : 'Offline'}
      </span>
    </div>
  );
};

export default StatusBadge;
