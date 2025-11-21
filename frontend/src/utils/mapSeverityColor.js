/**
 * Maps severity level to color classes
 * @param {string} severity - "high" | "med" | "low"
 * @returns {object} - Tailwind color classes
 */
export const mapSeverityColor = (severity) => {
  const colorMap = {
    high: {
      bg: 'bg-red-500/10',
      border: 'border-red-500/30',
      text: 'text-red-400',
      badge: 'bg-red-500',
      badgeText: 'text-white',
      dot: 'bg-red-500'
    },
    med: {
      bg: 'bg-amber-500/10',
      border: 'border-amber-500/30',
      text: 'text-amber-400',
      badge: 'bg-amber-500',
      badgeText: 'text-white',
      dot: 'bg-amber-500'
    },
    low: {
      bg: 'bg-blue-500/10',
      border: 'border-blue-500/30',
      text: 'text-blue-400',
      badge: 'bg-blue-500',
      badgeText: 'text-white',
      dot: 'bg-blue-500'
    }
  };

  return colorMap[severity] || colorMap.low;
};

/**
 * Maps alert type to icon and label
 */
export const mapAlertType = (alertType) => {
  const typeMap = {
    crowd: {
      label: 'Crowd Detected',
      icon: '👥'
    },
    fight: {
      label: 'Fight Detected',
      icon: '⚠️'
    },
    weapon: {
      label: 'Weapon Detected',
      icon: '🔫'
    }
  };

  return typeMap[alertType] || { label: alertType, icon: '⚡' };
};
