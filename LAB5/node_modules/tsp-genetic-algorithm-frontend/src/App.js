import React, { useState } from 'react';
import { logger } from './services/logger';
import Graph from './components/Graph/Graph';
import Controls from './components/Controls/Controls';
import Statistics from './components/Statistics/Statistics';
import LogViewer from './components/Logs/LogViewer';

function App() {
  const [selectedGraphId, setSelectedGraphId] = useState(null);
  const [algorithmStatus, setAlgorithmStatus] = useState(null);
  const [algorithmResults, setAlgorithmResults] = useState(null);

  const handleGraphSelect = (graphId) => {
    setSelectedGraphId(graphId);
    logger.info('Граф вибрано', { graphId });
  };

  const handleAlgorithmStatusChange = (status) => {
    setAlgorithmStatus(status);
    logger.info('Статус алгоритму змінено', { status });
  };

  const handleAlgorithmResultsUpdate = (results) => {
    setAlgorithmResults(results);
    logger.info('Отримано результати алгоритму', results);
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Паралельний Генетичний Алгоритм для TSP
          </h1>
        </div>
      </header>
      <main>
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <div className="lg:col-span-2">
                <Graph onGraphSelect={handleGraphSelect} />
              </div>
              <div className="space-y-4">
                <Controls 
                  graphId={selectedGraphId}
                  onStatusChange={handleAlgorithmStatusChange}
                  onResultsUpdate={handleAlgorithmResultsUpdate}
                />
                <Statistics 
                  runId={algorithmResults?.id}
                  status={algorithmStatus}
                />
              </div>
            </div>
            <div className="mt-4">
              <LogViewer />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App; 