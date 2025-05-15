import React, { useState, useEffect } from 'react';
import { algorithmApi } from '../../services/api';
import { ALGORITHM_STATUS } from '../../constants';
import { logger } from '../../services/logger';

const Controls = ({ graphId, onStatusChange, onResultsUpdate }) => {
  const [params, setParams] = useState({
    population_size: 100,
    mutation_rate: 0.1,
    elite_size: 10,
    max_generations: 1000,
    fitness_threshold: 0.001
  });

  const [runId, setRunId] = useState(null);
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);

  // Оновлення статусу
  useEffect(() => {
    if (!runId || status === ALGORITHM_STATUS.COMPLETED) return;

    const interval = setInterval(async () => {
      try {
        const statusData = await algorithmApi.getRunStatus(runId);
        setStatus(statusData.status);
        onStatusChange?.(statusData.status);

        if (statusData.status === ALGORITHM_STATUS.COMPLETED) {
          const results = await algorithmApi.getRunResults(runId);
          onResultsUpdate?.(results);
        }
      } catch (error) {
        logger.error('Помилка отримання статусу', error);
        setError('Помилка отримання статусу алгоритму');
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [runId, status, onStatusChange, onResultsUpdate]);

  const handleParamChange = (e) => {
    const { name, value } = e.target;
    setParams(prev => ({
      ...prev,
      [name]: Number(value)
    }));
  };

  const handleStart = async () => {
    if (!graphId) {
      setError('Спочатку створіть або виберіть граф');
      return;
    }

    try {
      setError(null);
      const run = await algorithmApi.createRun(graphId, params);
      setRunId(run.id);
      setStatus(ALGORITHM_STATUS.RUNNING);
      onStatusChange?.(ALGORITHM_STATUS.RUNNING);
      logger.info('Алгоритм запущено', { runId: run.id, params });
    } catch (error) {
      logger.error('Помилка запуску алгоритму', error);
      setError('Помилка запуску алгоритму: ' + (error.message || 'Невідома помилка'));
    }
  };

  const handleStop = async () => {
    if (!runId) return;

    try {
      setError(null);
      await algorithmApi.stopRun(runId);
      setStatus(ALGORITHM_STATUS.PAUSED);
      onStatusChange?.(ALGORITHM_STATUS.PAUSED);
      logger.info('Алгоритм зупинено', { runId });
    } catch (error) {
      logger.error('Помилка зупинки алгоритму', error);
      setError('Помилка зупинки алгоритму: ' + (error.message || 'Невідома помилка'));
    }
  };

  const handleResume = async () => {
    if (!runId) return;

    try {
      setError(null);
      await algorithmApi.resumeRun(runId);
      setStatus(ALGORITHM_STATUS.RUNNING);
      onStatusChange?.(ALGORITHM_STATUS.RUNNING);
      logger.info('Алгоритм відновлено', { runId });
    } catch (error) {
      logger.error('Помилка відновлення алгоритму', error);
      setError('Помилка відновлення алгоритму: ' + (error.message || 'Невідома помилка'));
    }
  };

  return (
    <div className="bg-white shadow rounded-lg p-4">
      <h2 className="text-xl font-semibold mb-4">Керування алгоритмом</h2>
      
      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Розмір популяції
          </label>
          <input
            type="number"
            name="population_size"
            value={params.population_size}
            onChange={handleParamChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            min="10"
            max="1000"
            disabled={!!runId}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Шанс мутації
          </label>
          <input
            type="number"
            name="mutation_rate"
            value={params.mutation_rate}
            onChange={handleParamChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            min="0.01"
            max="0.5"
            step="0.01"
            disabled={!!runId}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Розмір еліти
          </label>
          <input
            type="number"
            name="elite_size"
            value={params.elite_size}
            onChange={handleParamChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            min={Math.ceil(params.population_size * 0.01)}
            max={params.population_size}
            disabled={!!runId}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Максимум поколінь
          </label>
          <input
            type="number"
            name="max_generations"
            value={params.max_generations}
            onChange={handleParamChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            min="1"
            max="10000"
            disabled={!!runId}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Поріг придатності
          </label>
          <input
            type="number"
            name="fitness_threshold"
            value={params.fitness_threshold}
            onChange={handleParamChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            min="0"
            max="1"
            step="0.001"
            disabled={!!runId}
          />
        </div>

        <div className="flex space-x-2">
          {!runId && (
            <button
              onClick={handleStart}
              disabled={!graphId}
              className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Запустити
            </button>
          )}
          {runId && status === ALGORITHM_STATUS.RUNNING && (
            <button
              onClick={handleStop}
              className="flex-1 bg-yellow-600 text-white px-4 py-2 rounded-md hover:bg-yellow-700"
            >
              Зупинити
            </button>
          )}
          {runId && status === ALGORITHM_STATUS.PAUSED && (
            <button
              onClick={handleResume}
              className="flex-1 bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
            >
              Відновити
            </button>
          )}
        </div>

        {status && (
          <div className="mt-4 p-2 bg-gray-100 rounded text-center">
            Статус: {status}
          </div>
        )}
      </div>
    </div>
  );
};

export default Controls; 