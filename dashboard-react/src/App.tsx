import React from 'react';
import './App.css';
import ChurnData from './ChurnData';

function App() {
  // For now, we'll use a static value for the churn rate.
  const churnRate = 15.5;

  return (
    <div className="App">
      <header className="App-header">
        <h1>Telco Customer Churn Dashboard</h1>
      </header>
      <p>Welcome! Your dashboard will display churn analysis data here.</p>
      <ChurnData churnRate={churnRate} />
    </div>
  );
}

export default App;
