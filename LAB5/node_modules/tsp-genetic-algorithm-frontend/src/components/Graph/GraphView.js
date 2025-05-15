import React, { useState, useEffect } from 'react';
import { graphService } from '../../services/api';

const GraphView = ({ graphId, onGraphSelect }) => {
    const [graphs, setGraphs] = useState([]);
    const [selectedGraph, setSelectedGraph] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Завантаження списку графів
    useEffect(() => {
        loadGraphs();
    }, []);

    // Завантаження вибраного графа
    useEffect(() => {
        if (graphId) {
            loadGraph(graphId);
        }
    }, [graphId]);

    const loadGraphs = async () => {
        try {
            setLoading(true);
            const data = await graphService.getGraphs();
            setGraphs(data);
            setError(null);
        } catch (error) {
            setError('Помилка завантаження списку графів');
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const loadGraph = async (id) => {
        try {
            setLoading(true);
            const graph = await graphService.getGraph(id);
            setSelectedGraph(graph);
            onGraphSelect(graph);
            setError(null);
        } catch (error) {
            setError('Помилка завантаження графа');
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const handleGraphSelect = (e) => {
        const id = e.target.value;
        if (id) {
            loadGraph(id);
        } else {
            setSelectedGraph(null);
            onGraphSelect(null);
        }
    };

    if (loading) {
        return <div>Завантаження...</div>;
    }

    if (error) {
        return <div className="error">{error}</div>;
    }

    return (
        <div className="graph-view">
            <div className="graph-selector">
                <label>Виберіть граф:</label>
                <select 
                    value={selectedGraph?.id || ''} 
                    onChange={handleGraphSelect}
                >
                    <option value="">Виберіть граф...</option>
                    {graphs.map(graph => (
                        <option key={graph.id} value={graph.id}>
                            {graph.name}
                        </option>
                    ))}
                </select>
            </div>

            {selectedGraph && (
                <div className="graph-details">
                    <h3>{selectedGraph.name}</h3>
                    <div className="graph-info">
                        <p>Кількість вершин: {selectedGraph.nodes.length}</p>
                        <p>Кількість ребер: {selectedGraph.edges.length}</p>
                    </div>
                    <div className="graph-structure">
                        <h4>Вершини:</h4>
                        <div className="nodes">
                            {selectedGraph.nodes.map(node => (
                                <span key={node} className="node">{node}</span>
                            ))}
                        </div>
                        <h4>Ребра:</h4>
                        <div className="edges">
                            {selectedGraph.edges.map((edge, index) => (
                                <div key={index} className="edge">
                                    {edge.from_node} → {edge.to_node} ({edge.weight})
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default GraphView; 