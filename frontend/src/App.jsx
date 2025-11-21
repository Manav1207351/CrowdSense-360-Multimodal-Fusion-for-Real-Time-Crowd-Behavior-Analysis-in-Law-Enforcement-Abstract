import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Analytics from './pages/Analytics';
import './index.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/analytics" element={<Analytics />} />
      </Routes>
    </Router>
  );
}

export default App;
