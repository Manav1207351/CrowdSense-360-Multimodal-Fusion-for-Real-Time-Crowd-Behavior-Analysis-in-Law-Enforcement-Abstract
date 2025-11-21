/**
 * Formats a timestamp for display
 * @param {string} timestamp - ISO timestamp from backend
 * @returns {string} - Human readable time like "2 min ago"
 */
export const formatTime = (timestamp) => {
  const now = new Date();
  const time = new Date(timestamp);
  const diff = Math.floor((now - time) / 1000); // seconds

  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
};

/**
 * Formats timestamp to time only (HH:MM:SS)
 */
export const formatTimeOnly = (timestamp) => {
  const time = new Date(timestamp);
  return time.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit',
    second: '2-digit',
    hour12: false 
  });
};

/**
 * Gets current time formatted
 */
export const getCurrentTime = () => {
  const now = new Date();
  return now.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit',
    second: '2-digit',
    hour12: false 
  });
};

/**
 * Gets current date formatted
 */
export const getCurrentDate = () => {
  const now = new Date();
  return now.toLocaleDateString('en-US', { 
    weekday: 'long',
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });
};
