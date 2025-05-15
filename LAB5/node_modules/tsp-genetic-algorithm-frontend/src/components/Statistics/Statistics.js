import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

const Statistics = () => {
  // Приклад даних для демонстрації
  const data = [
    { generation: 0, best: 1000, average: 1200, worst: 1500 },
    { generation: 100, best: 800, average: 1000, worst: 1300 },
    { generation: 200, best: 600, average: 800, worst: 1100 },
    { generation: 300, best: 500, average: 700, worst: 900 },
    { generation: 400, best: 450, average: 600, worst: 800 },
  ];

  return (
    <div className="bg-white shadow rounded-lg p-4">
      <h2 className="text-xl font-semibold mb-4">Статистика еволюції</h2>
      
      <div className="h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="generation" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="best"
              stroke="#2563eb"
              name="Найкращий"
            />
            <Line
              type="monotone"
              dataKey="average"
              stroke="#16a34a"
              name="Середній"
            />
            <Line
              type="monotone"
              dataKey="worst"
              stroke="#dc2626"
              name="Найгірший"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 space-y-2">
        <div className="flex justify-between">
          <span className="text-gray-600">Поточне покоління:</span>
          <span className="font-medium">400</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">Найкраща відстань:</span>
          <span className="font-medium">450</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">Середня відстань:</span>
          <span className="font-medium">600</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">Час виконання:</span>
          <span className="font-medium">1.5 сек</span>
        </div>
      </div>

      <div className="mt-4">
        <button className="w-full bg-gray-100 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-200">
          Експорт статистики
        </button>
      </div>
    </div>
  );
};

export default Statistics; 