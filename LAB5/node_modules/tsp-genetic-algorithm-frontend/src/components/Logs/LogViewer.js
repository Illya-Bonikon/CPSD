import React, { useState, useEffect, useRef, useCallback } from 'react';
import { logger, LogLevel } from '../../services/logger';
import './LogViewer.css';

const LogViewer = () => {
    const [logs, setLogs] = useState([]);
    const [filter, setFilter] = useState(LogLevel.DEBUG);
    const [searchQuery, setSearchQuery] = useState('');
    const [autoScroll, setAutoScroll] = useState(true);
    const [isExporting, setIsExporting] = useState(false);
    const [error, setError] = useState(null);
    const logContainerRef = useRef(null);

    // Підписка на оновлення логів
    useEffect(() => {
        const unsubscribe = logger.subscribe((log) => {
            if (log === null) {
                // Очищення логів
                setLogs([]);
            } else {
                setLogs(prevLogs => [...prevLogs, log]);
            }
        });

        return () => unsubscribe();
    }, []);

    // Автопрокрутка
    useEffect(() => {
        if (autoScroll && logContainerRef.current) {
            logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
        }
    }, [logs, autoScroll]);

    // Фільтрація логів
    const filteredLogs = logs.filter(log => {
        const matchesFilter = log.level === filter;
        const matchesSearch = searchQuery === '' || 
            log.message.toLowerCase().includes(searchQuery.toLowerCase()) ||
            (log.data && JSON.stringify(log.data).toLowerCase().includes(searchQuery.toLowerCase()));
        return matchesFilter && matchesSearch;
    });

    // Обробники подій
    const handleFilterChange = useCallback((event) => {
        setFilter(event.target.value);
        setError(null);
    }, []);

    const handleSearchChange = useCallback((event) => {
        setSearchQuery(event.target.value);
        setError(null);
    }, []);

    const handleClearLogs = useCallback(() => {
        if (window.confirm('Ви впевнені, що хочете очистити всі логи?')) {
            try {
                logger.clearLogs();
                setError(null);
            } catch (err) {
                setError('Помилка при очищенні логів: ' + err.message);
                logger.error('Помилка при очищенні логів', err);
            }
        }
    }, []);

    const handleAutoScrollChange = useCallback(() => {
        setAutoScroll(prev => !prev);
    }, []);

    const handleExportLogs = useCallback(async () => {
        if (filteredLogs.length === 0) {
            setError('Немає логів для експорту');
            return;
        }

        setIsExporting(true);
        setError(null);

        try {
            const logText = filteredLogs.map(log => log.toString()).join('\n');
            const blob = new Blob([logText], { type: 'text/plain;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `logs-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            logger.info('Логи успішно експортовано', { count: filteredLogs.length });
        } catch (err) {
            setError('Помилка при експорті логів: ' + err.message);
            logger.error('Помилка при експорті логів', err);
        } finally {
            setIsExporting(false);
        }
    }, [filteredLogs]);

    // Очищення помилки при зміні фільтрів
    useEffect(() => {
        setError(null);
    }, [filter, searchQuery]);

    return (
        <div className="log-viewer">
            <div className="log-controls">
                <div className="log-filter">
                    <label>
                        Рівень логування:
                        <select 
                            value={filter} 
                            onChange={handleFilterChange}
                            disabled={isExporting}
                        >
                            {Object.values(LogLevel).map(level => (
                                <option key={level} value={level}>{level}</option>
                            ))}
                        </select>
                    </label>
                    <input
                        type="text"
                        placeholder="Пошук по логах..."
                        value={searchQuery}
                        onChange={handleSearchChange}
                        disabled={isExporting}
                    />
                </div>
                <div className="log-actions">
                    <label className="auto-scroll">
                        <input
                            type="checkbox"
                            checked={autoScroll}
                            onChange={handleAutoScrollChange}
                            disabled={isExporting}
                        />
                        Автопрокрутка
                    </label>
                    <button 
                        onClick={handleClearLogs} 
                        className="clear-logs"
                        disabled={isExporting || logs.length === 0}
                    >
                        Очистити логи
                    </button>
                    <button 
                        onClick={handleExportLogs} 
                        className="export-logs"
                        disabled={isExporting || filteredLogs.length === 0}
                    >
                        {isExporting ? 'Експорт...' : 'Експорт логів'}
                    </button>
                </div>
            </div>
            {error && (
                <div className="log-error-message">
                    {error}
                </div>
            )}
            <div className="log-container" ref={logContainerRef}>
                {filteredLogs.map(log => (
                    <div
                        key={log.id}
                        className={`log-entry log-${log.level.toLowerCase()}`}
                        dangerouslySetInnerHTML={{ __html: log.toHTML() }}
                    />
                ))}
                {filteredLogs.length === 0 && (
                    <div className="no-logs">
                        {searchQuery 
                            ? 'Немає логів, що відповідають пошуковому запиту'
                            : 'Немає логів для відображення'}
                    </div>
                )}
            </div>
        </div>
    );
};

export default LogViewer; 