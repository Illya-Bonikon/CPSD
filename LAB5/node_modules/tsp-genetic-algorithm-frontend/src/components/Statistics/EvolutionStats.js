import React, { useState, useEffect } from 'react';
import { algorithmService } from '../../services/api';
import { ALGORITHM_STATUS } from '../../constants';

const EvolutionStats = ({ runId }) => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (runId) {
            const interval = setInterval(loadStats, 2000);
            return () => clearInterval(interval);
        }
    }, [runId]);

    const loadStats = async () => {
        if (!runId) return;
        
        try {
            setLoading(true);
            const data = await algorithmService.getEvolutionStats(runId);
            setStats(data);
            setError(null);
        } catch (error) {
            setError('Помилка завантаження статистики');
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    if (!runId) {
        return <div>Виберіть граф та запустіть алгоритм</div>;
    }

    if (loading && !stats) {
        return <div>Завантаження статистики...</div>;
    }

    if (error) {
        return <div className="error">{error}</div>;
    }

    if (!stats) {
        return null;
    }

    return (
        <div className="evolution-stats">
            <h3>Статистика еволюції</h3>
            
            <div className="current-generation">
                <h4>Поточне покоління: {stats.current_generation}</h4>
                <div className="generation-stats">
                    <div className="stat-item">
                        <label>Найкраща придатність:</label>
                        <span>{stats.best_fitness.toFixed(2)}</span>
                    </div>
                    <div className="stat-item">
                        <label>Середня придатність:</label>
                        <span>{stats.average_fitness.toFixed(2)}</span>
                    </div>
                    <div className="stat-item">
                        <label>Найгірша придатність:</label>
                        <span>{stats.worst_fitness.toFixed(2)}</span>
                    </div>
                </div>
            </div>

            <div className="best-path">
                <h4>Найкращий знайдений шлях:</h4>
                <div className="path">
                    {stats.best_path.join(' → ')}
                </div>
                <div className="path-length">
                    Довжина шляху: {stats.best_path_length.toFixed(2)}
                </div>
            </div>

            <div className="evolution-progress">
                <h4>Прогрес еволюції:</h4>
                <div className="progress-bar">
                    <div 
                        className="progress-fill"
                        style={{ 
                            width: `${(stats.current_generation / stats.max_generations) * 100}%` 
                        }}
                    />
                </div>
                <div className="progress-text">
                    {stats.current_generation} / {stats.max_generations} поколінь
                </div>
            </div>

            {stats.status === ALGORITHM_STATUS.COMPLETED && (
                <div className="completion-info">
                    <h4>Алгоритм завершено</h4>
                    <p>Час виконання: {stats.execution_time.toFixed(2)} секунд</p>
                    <p>Причина зупинки: {stats.stop_reason}</p>
                </div>
            )}
        </div>
    );
};

export default EvolutionStats; 