import React from 'react';

const Sidebar = ({ selectedCamera, onSelectCamera, cameras }) => {
  return (
    <aside className="w-64 bg-dark-surface border-r border-dark-border p-4">
      <h2 className="text-lg font-bold text-white mb-4">Cameras</h2>
      <div className="space-y-2">
        {cameras.map((camera) => (
          <button
            key={camera.id}
            onClick={() => onSelectCamera(camera.id)}
            className={`w-full text-left p-3 rounded-lg transition-all ${
              selectedCamera === camera.id
                ? 'bg-blue-500/20 border border-blue-500/50'
                : 'bg-dark-hover border border-dark-border hover:bg-dark-border'
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="font-medium text-white">{camera.name}</span>
              <div className="flex items-center gap-2">
                <div
                  className={`w-2 h-2 rounded-full ${
                    camera.status === 'online' ? 'bg-green-500 animate-pulse' : 'bg-red-500'
                  }`}
                />
                <span
                  className={`text-xs px-2 py-0.5 rounded ${
                    camera.status === 'online'
                      ? 'bg-green-500/20 text-green-400'
                      : 'bg-red-500/20 text-red-400'
                  }`}
                >
                  {camera.status === 'online' ? 'Online' : 'Offline'}
                </span>
              </div>
            </div>
          </button>
        ))}
      </div>
    </aside>
  );
};

export default Sidebar;
