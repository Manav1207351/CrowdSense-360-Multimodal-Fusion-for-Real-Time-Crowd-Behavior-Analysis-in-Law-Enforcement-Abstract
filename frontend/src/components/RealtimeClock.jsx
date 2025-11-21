import React, { useState, useEffect } from 'react';
import { getCurrentTime, getCurrentDate } from '../utils/formatTime';

const RealtimeClock = () => {
  const [time, setTime] = useState(getCurrentTime());
  const [date, setDate] = useState(getCurrentDate());

  useEffect(() => {
    const interval = setInterval(() => {
      setTime(getCurrentTime());
      setDate(getCurrentDate());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="text-right">
      <div className="text-sm text-gray-400">{date}</div>
      <div className="text-2xl font-bold text-white">{time}</div>
    </div>
  );
};

export default RealtimeClock;
