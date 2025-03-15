import React from 'react';

interface ChurnDataProps {
  churnRate: number;
}

const ChurnData: React.FC<ChurnDataProps> = ({ churnRate }) => {
  return (
    <div>
      <h2>Churn Rate</h2>
      <p>The current churn rate is: {churnRate}%</p>
    </div>
  );
};

export default ChurnData;
