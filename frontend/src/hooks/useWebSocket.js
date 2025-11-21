import { useWebSocketContext } from '../context/WebSocketContext';

/**
 * Custom hook to access WebSocket data and connection status
 */
export const useWebSocket = () => {
  const { ws, connected, cameras, timeline, alerts } = useWebSocketContext();

  return {
    ws,
    connected,
    cameras,
    timeline,
    alerts,
  };
};
