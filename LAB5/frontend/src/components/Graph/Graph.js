import React, { useRef, useState, useEffect } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { graphApi } from '../../services/api';
import { logger } from '../../services/logger';

const Graph = ({ onGraphSelect }) => {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [graphs, setGraphs] = useState([]);
  const [selectedGraphId, setSelectedGraphId] = useState(null);
  const [error, setError] = useState(null);
  const graphRef = useRef();

  // Завантаження списку графів при монтуванні компонента
  useEffect(() => {
    const loadGraphs = async () => {
      try {
        const data = await graphApi.getAllGraphs();
        setGraphs(data);
        logger.info('Список графів завантажено успішно');
      } catch (error) {
        logger.error('Помилка при завантаженні списку графів', error);
        setError('Не вдалося завантажити список графів');
      }
    };

    loadGraphs();
  }, []);

  // Завантаження графа при виборі
  useEffect(() => {
    const loadGraph = async (graphId) => {
      if (!graphId) return;
      
      try {
        setError(null);
        const data = await graphApi.getGraph(graphId);
        if (data) {
          const formattedData = {
            nodes: data.nodes.map(node => ({
              id: node.id,
              x: node.x,
              y: node.y
            })),
            links: data.edges.map(edge => ({
              source: edge.source,
              target: edge.target,
              weight: edge.weight
            }))
          };
          setGraphData(formattedData);
          logger.info('Граф завантажено успішно', { graphId });
        }
      } catch (error) {
        logger.error('Помилка при завантаженні графа', error);
        setError('Не вдалося завантажити граф');
        setGraphData({ nodes: [], links: [] });
      }
    };

    if (selectedGraphId) {
      loadGraph(selectedGraphId);
    }
  }, [selectedGraphId]);

  const handleGraphSelect = (graphId) => {
    setSelectedGraphId(graphId);
    if (onGraphSelect) {
      onGraphSelect(graphId);
    }
  };

  return (
    <div className="bg-white shadow rounded-lg p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Візуалізація графа</h2>
        <select
          className="form-select rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          value={selectedGraphId || ''}
          onChange={(e) => handleGraphSelect(e.target.value)}
        >
          <option value="">Виберіть граф</option>
          {graphs.map((graph) => (
            <option key={graph.id} value={graph.id}>
              Граф {graph.id}
            </option>
          ))}
        </select>
      </div>
      {error && (
        <div className="mb-4 p-4 bg-red-50 text-red-700 rounded-md">
          {error}
        </div>
      )}
      <div className="h-[600px] border rounded-lg">
        <ForceGraph2D
          ref={graphRef}
          graphData={graphData}
          nodeLabel="id"
          nodeColor={() => '#1a56db'}
          linkColor={() => '#e5e7eb'}
          nodeRelSize={6}
          linkWidth={1}
          linkDirectionalParticles={2}
          linkDirectionalParticleSpeed={0.005}
        />
      </div>
    </div>
  );
};

export default Graph; 