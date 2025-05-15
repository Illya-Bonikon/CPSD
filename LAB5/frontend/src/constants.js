// Константи для API
export const API = {
    BASE_URL: process.env.VITE_API_URL || 'http://localhost:8000/api/v1',
    ENDPOINTS: {
        GRAPHS: '/graphs',
        ALGORITHM: '/algorithm/runs',
        GENERATIONS: '/generations',
        STATS: '/stats',
    },
};

// Константи для статусів алгоритму
export const ALGORITHM_STATUS = {
    PENDING: 'pending',
    RUNNING: 'running',
    PAUSED: 'paused',
    COMPLETED: 'completed',
    FAILED: 'failed',
};

// Константи для налаштувань алгоритму за замовчуванням
export const DEFAULT_ALGORITHM_PARAMS = {
    POPULATION_SIZE: 100,
    MUTATION_RATE: 0.1,
    ELITE_SIZE: 10,
    MAX_GENERATIONS: 1000,
    FITNESS_THRESHOLD: 0.001,
};

// Константи для пагінації
export const PAGINATION = {
    DEFAULT_PAGE_SIZE: 10,
    PAGE_SIZES: [10, 20, 50, 100],
};

// Константи для повідомлень
export const MESSAGES = {
    ERRORS: {
        SERVER_ERROR: 'Помилка сервера',
        NETWORK_ERROR: 'Помилка мережі',
        NOT_FOUND: 'Ресурс не знайдено',
        VALIDATION_ERROR: 'Помилка валідації',
    },
    SUCCESS: {
        GRAPH_CREATED: 'Граф успішно створено',
        GRAPH_UPDATED: 'Граф успішно оновлено',
        GRAPH_DELETED: 'Граф успішно видалено',
        ALGORITHM_STARTED: 'Алгоритм запущено',
        ALGORITHM_PAUSED: 'Алгоритм призупинено',
        ALGORITHM_RESUMED: 'Алгоритм відновлено',
    },
}; 