// Рівні логування
export const LogLevel = {
    DEBUG: 'DEBUG',
    INFO: 'INFO',
    WARNING: 'WARNING',
    ERROR: 'ERROR'
};

// Кольори для різних рівнів логування
const LOG_COLORS = {
    [LogLevel.DEBUG]: '#6c757d',    // сірий
    [LogLevel.INFO]: '#0d6efd',     // синій
    [LogLevel.WARNING]: '#ffc107',  // жовтий
    [LogLevel.ERROR]: '#dc3545'     // червоний
};

// Клас для логу
class LogEntry {
    constructor(level, message, data = null, timestamp = new Date()) {
        this.level = level;
        this.message = message;
        this.data = data;
        this.timestamp = timestamp;
        this.id = Math.random().toString(36).substr(2, 9);
    }

    toString() {
        const time = this.timestamp.toLocaleTimeString();
        const dataStr = this.data ? `\n${JSON.stringify(this.data, null, 2)}` : '';
        return `[${time}] ${this.level}: ${this.message}${dataStr}`;
    }

    toHTML() {
        const time = this.timestamp.toLocaleTimeString();
        const dataStr = this.data ? `<pre>${JSON.stringify(this.data, null, 2)}</pre>` : '';
        return `
            <div class="log-entry log-${this.level.toLowerCase()}" data-id="${this.id}">
                <span class="log-time">[${time}]</span>
                <span class="log-level">${this.level}</span>
                <span class="log-message">${this.message}</span>
                ${dataStr}
            </div>
        `;
    }
}

// Синглтон для логування
class Logger {
    constructor() {
        this.logs = [];
        this.maxLogs = 1000; // максимальна кількість збережених логів
        this.listeners = new Set();
        this.minLevel = LogLevel.DEBUG; // мінімальний рівень логування
    }

    // Додавання нового логу
    _addLog(level, message, data = null) {
        if (this._shouldLog(level)) {
            const log = new LogEntry(level, message, data);
            this.logs.push(log);
            
            // Обмеження кількості логів
            if (this.logs.length > this.maxLogs) {
                this.logs.shift();
            }

            // Сповіщення слухачів
            this._notifyListeners(log);

            // Виведення в консоль
            this._consoleLog(level, message, data);
        }
    }

    // Перевірка чи потрібно логувати
    _shouldLog(level) {
        const levels = Object.values(LogLevel);
        return levels.indexOf(level) >= levels.indexOf(this.minLevel);
    }

    // Виведення в консоль
    _consoleLog(level, message, data) {
        const color = LOG_COLORS[level];
        const style = `color: ${color}; font-weight: bold;`;
        
        if (data) {
            console.log(`%c${level}: ${message}`, style, data);
        } else {
            console.log(`%c${level}: ${message}`, style);
        }
    }

    // Сповіщення слухачів
    _notifyListeners(log) {
        this.listeners.forEach(listener => listener(log));
    }

    // Методи логування
    debug(message, data = null) {
        this._addLog(LogLevel.DEBUG, message, data);
    }

    info(message, data = null) {
        this._addLog(LogLevel.INFO, message, data);
    }

    warning(message, data = null) {
        this._addLog(LogLevel.WARNING, message, data);
    }

    error(message, data = null) {
        this._addLog(LogLevel.ERROR, message, data);
    }

    // Отримання всіх логів
    getLogs() {
        return [...this.logs];
    }

    // Очищення логів
    clearLogs() {
        this.logs = [];
        this._notifyListeners(null); // сповіщення про очищення
    }

    // Встановлення мінімального рівня логування
    setMinLevel(level) {
        if (Object.values(LogLevel).includes(level)) {
            this.minLevel = level;
        }
    }

    // Підписка на оновлення логів
    subscribe(listener) {
        this.listeners.add(listener);
        return () => this.listeners.delete(listener); // функція для відписки
    }

    // Фільтрація логів за рівнем
    filterByLevel(level) {
        return this.logs.filter(log => log.level === level);
    }

    // Пошук по логах
    search(query) {
        const searchStr = query.toLowerCase();
        return this.logs.filter(log => 
            log.message.toLowerCase().includes(searchStr) ||
            (log.data && JSON.stringify(log.data).toLowerCase().includes(searchStr))
        );
    }
}

// Експортуємо єдиний екземпляр логера
export const logger = new Logger();

// Хук для використання логера в компонентах
export const useLogger = () => {
    const log = (level, message, data = null) => {
        logger.addLog(level, message, data);
    };

    return {
        log,
        info: (message, data) => log(LogLevel.INFO, message, data),
        warn: (message, data) => log(LogLevel.WARNING, message, data),
        error: (message, data) => log(LogLevel.ERROR, message, data),
        debug: (message, data) => log(LogLevel.DEBUG, message, data),
        getLogs: logger.getLogs,
        clearLogs: logger.clearLogs,
        getLogsByLevel: logger.filterByLevel,
        getRecentLogs: logger.getLogs
    };
}; 