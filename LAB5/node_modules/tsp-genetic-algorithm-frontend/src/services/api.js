import axios from 'axios';
import { logger } from './logger';

// Базовий URL API з змінних середовища React
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// Створюємо екземпляр axios з базовою конфігурацією
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Обробник помилок API
const handleApiError = (error, context) => {
  const apiError = {
    message: error.response?.data?.message || error.message || 'Помилка API',
    status: error.response?.status,
    context,
  };
  
  logger.error(`API помилка (${context}):`, apiError);
  throw apiError;
};

// API для роботи з графами
export const graphApi = {
  // Отримати список всіх графів  
  getAllGraphs: async () => {
    try {
      logger.info('Отримання списку графів');
      const response = await api.get('/graphs');
      logger.info('Список графів отримано успішно');
      return response.data;
    } catch (error) {
      return handleApiError(error, 'getAllGraphs');
    }
  },

  // Отримати граф за ID
  getGraph: async (id) => {
    try {
      logger.info(`Отримання графу з ID: ${id}`);
      const response = await api.get(`/graphs/${id}`);
      logger.info(`Граф з ID ${id} отримано успішно`);
      return response.data;
    } catch (error) {
      return handleApiError(error, 'getGraph');
    }
  },

  // Створити новий граф
  createGraph: async (graphData) => {
    try {
      logger.info('Створення нового графу:', graphData);
      const response = await api.post('/graphs', graphData);
      logger.info('Граф створено успішно:', response.data);
      return response.data;
    } catch (error) {
      return handleApiError(error, 'createGraph');
    }
  },

  // Видалити граф
  deleteGraph: async (id) => {
    try {
      logger.info(`Видалення графу з ID: ${id}`);
      await api.delete(`/graphs/${id}`);
      logger.info(`Граф з ID ${id} видалено успішно`);
    } catch (error) {
      return handleApiError(error, 'deleteGraph');
    }
  },
};

// API для роботи з алгоритмом
export const algorithmApi = {
  // Створити новий запуск алгоритму
  createRun: async ({ graphId, params }) => {
    try {
      logger.info('Створення нового запуску алгоритму:', { graphId, params });
      const response = await api.post('/algorithm/runs', {
        graph_id: graphId,
        ...params,
      });
      logger.info('Запуск алгоритму створено успішно:', response.data);
      return response.data;
    } catch (error) {
      return handleApiError(error, 'createRun');
    }
  },

  // Отримати статус запуску
  getRunStatus: async (runId) => {
    try {
      logger.info(`Отримання статусу запуску з ID: ${runId}`);
      const response = await api.get(`/algorithm/runs/${runId}/status`);
      logger.info(`Статус запуску отримано успішно:`, response.data);
      return response.data;
    } catch (error) {
      return handleApiError(error, 'getRunStatus');
    }
  },

  // Отримати результати запуску
  getRunResults: async (runId) => {
    try {
      logger.info(`Отримання результатів запуску з ID: ${runId}`);
      const response = await api.get(`/algorithm/runs/${runId}/results`);
      logger.info(`Результати запуску отримано успішно:`, response.data);
      return response.data;
    } catch (error) {
      return handleApiError(error, 'getRunResults');
    }
  },

  // Зупинити запуск
  stopRun: async (runId) => {
    try {
      logger.info(`Зупинка запуску з ID: ${runId}`);
      await api.post(`/algorithm/runs/${runId}/stop`);
      logger.info(`Запуск з ID ${runId} зупинено успішно`);
    } catch (error) {
      return handleApiError(error, 'stopRun');
    }
  },

  // Відновити запуск
  resumeRun: async (runId) => {
    try {
      logger.info(`Відновлення запуску з ID: ${runId}`);
      await api.post(`/algorithm/runs/${runId}/resume`);
      logger.info(`Запуск з ID ${runId} відновлено успішно`);
    } catch (error) {
      return handleApiError(error, 'resumeRun');
    }
  },
}; 