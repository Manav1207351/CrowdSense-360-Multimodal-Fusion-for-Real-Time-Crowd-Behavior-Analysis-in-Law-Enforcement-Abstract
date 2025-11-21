/**
 * Initial timeline data (last 15 minutes)
 */
export const initialTimeline = Array.from({ length: 15 }, (_, i) => ({
  minute: -14 + i,
  events: 0,
  label: `${-14 + i}m`
}));
