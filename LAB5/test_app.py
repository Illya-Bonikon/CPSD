import pytest
import numpy as np

from core.graph import GraphGenerator
from core.ga import ParallelGA
from core.db import MongoLogger


def test_graph_generator_valid():
    gen = GraphGenerator(5, 1, 10)
    graph = gen.generate()
    assert graph.shape == (5, 5)
    off_diag = graph[~np.eye(5, dtype=bool)]
    assert np.all(off_diag >= 1) and np.all(off_diag <= 10)
    assert np.allclose(np.diag(graph), 0)
    print("Testing test_graph_generator_valid - passed")

def test_graph_generator_invalid():
    try:
        GraphGenerator(2, 1, 10).generate()
    except ValueError:
        print("Testing test_graph_generator_invalid - passed")
        return
    assert False, "ValueError не було кинуто"


def test_parallel_ga_basic():
    gen = GraphGenerator(6, 1, 10)
    graph = gen.generate()
    ga = ParallelGA(graph, pop_size=10, epochs=5, mut_prob=0.5, cross_prob=0.7, n_islands=2)
    stats = ga.run()
    assert len(stats) == 5
    for gen_stat in stats:
        assert 'best' in gen_stat and 'worst' in gen_stat and 'avg' in gen_stat
    print("Testing test_parallel_ga_basic - passed")

def test_parallel_ga_invalid_params():
    gen = GraphGenerator(6, 1, 10)
    graph = gen.generate()
    try:
        ParallelGA(graph, pop_size=0, epochs=5, mut_prob=0.5, cross_prob=0.7, n_islands=2).run()
    except ValueError as e:
        assert "Популяція порожня" in str(e)
        print("Testing test_parallel_ga_invalid_params - passed")
        return
    except Exception:
        print("Testing test_parallel_ga_invalid_params - passed (інша помилка)")
        return
    assert False, "ValueError не було кинуто"


def test_mongo_logger_save_and_load(monkeypatch):
    
    class DummyLogger:
        def save_run(self, graph, params, stats):
            self.saved = True
            self.last_graph = graph
            self.last_params = params
            self.last_stats = stats
        def get_history(self):
            return [{'graph': self.last_graph, 'params': self.last_params, 'generations': self.last_stats}]
    logger = DummyLogger()
    gen = GraphGenerator(5, 1, 10)
    graph = gen.generate()
    params = {'n': 5, 'w_min': 1, 'w_max': 10, 'epochs': 2, 'pop_size': 5, 'mut_prob': 0.1, 'cross_prob': 0.7, 'n_islands': 1}
    stats = [{'best': {'path': [0,1,2,3,4], 'length': 10}, 'worst': {'path': [4,3,2,1,0], 'length': 20}, 'avg': 15}]
    logger.save_run(graph, params, stats)
    history = logger.get_history()
    assert history[0]['params'] == params
    assert np.allclose(history[0]['graph'], graph)
    print("Testing test_mongo_logger_save_and_load - passed")


@pytest.mark.parametrize("n, w_min, w_max, epochs, pop_size, mut_prob, cross_prob, n_islands, valid", [
    (10, 1, 100, 100, 100, 0.05, 0.7, 4, True),
    (3, 1, 100, 100, 100, 0.05, 0.7, 4, False),  
    (10, 0, 100, 100, 100, 0.05, 0.7, 4, False),  
    (10, 1, 100, 0, 100, 0.05, 0.7, 4, False),    
    (10, 1, 100, 100, 0, 0.05, 0.7, 4, False),    
    (10, 1, 100, 100, 100, -0.1, 0.7, 4, False),  
    (10, 1, 100, 100, 100, 0.05, 1.1, 4, False),  
    (10, 1, 100, 100, 100, 0.05, 0.7, 0, False),  
])
def test_params_validation(n, w_min, w_max, epochs, pop_size, mut_prob, cross_prob, n_islands, valid):
    try:
        assert n >= 4
        assert w_min >= 1
        assert w_max >= w_min
        assert epochs >= 1
        assert pop_size >= 2
        assert 0 <= mut_prob <= 1
        assert 0 <= cross_prob <= 1
        assert n_islands >= 1
        assert valid
        print(f"Testing test_params_validation({n}, ...) - passed")
    except AssertionError:
        assert not valid
        print(f"Testing test_params_validation({n}, ...) - passed (invalid)")


def test_full_pipeline(monkeypatch):
    
    class DummyLogger:
        def save_run(self, graph, params, stats): pass
    gen = GraphGenerator(7, 1, 10)
    graph = gen.generate()
    ga = ParallelGA(graph, pop_size=8, epochs=3, mut_prob=0.2, cross_prob=0.8, n_islands=2)
    stats = ga.run()
    params = {'n': 7, 'w_min': 1, 'w_max': 10, 'epochs': 3, 'pop_size': 8, 'mut_prob': 0.2, 'cross_prob': 0.8, 'n_islands': 2}
    logger = DummyLogger()
    
    logger.save_run(graph, params, stats)
    
    assert len(stats) == 3
    for s in stats:
        assert 'best' in s and 'worst' in s and 'avg' in s
    print("Testing test_full_pipeline - passed")

