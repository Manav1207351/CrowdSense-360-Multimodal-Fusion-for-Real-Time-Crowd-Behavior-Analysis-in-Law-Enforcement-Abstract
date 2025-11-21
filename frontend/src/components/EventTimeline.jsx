import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { initialTimeline } from '../data/initialTimeline';

const EventTimeline = () => {
  const timeline = initialTimeline;

  return (
    <div className="bg-dark-surface border border-dark-border rounded-lg p-6">
      <h3 className="text-lg font-bold text-white mb-4">
        Event Timeline (Last 15 Minutes)
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={timeline}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e2533" />
          <XAxis
            dataKey="label"
            stroke="#6b7280"
            tick={{ fill: '#9ca3af', fontSize: 12 }}
          />
          <YAxis
            stroke="#6b7280"
            tick={{ fill: '#9ca3af', fontSize: 12 }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#131824',
              border: '1px solid #1e2533',
              borderRadius: '8px',
            }}
            labelStyle={{ color: '#fff' }}
            itemStyle={{ color: '#3b82f6' }}
          />
          <Bar dataKey="events" fill="#3b82f6" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default EventTimeline;
