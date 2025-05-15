import pytest
from app.models.graph import Graph, Edge
from app.algorithms.genetic import Chromosome, GeneticAlgorithm

@pytest.fixture
def sample_graph():
    """
    Створення тестового графа для перевірки алгоритму.
    """
    nodes = [0, 1, 2, 3]
    edges = [
        Edge(from_node=0, to_node=1, weight=10),
        Edge(from_node=1, to_node=2, weight=15),
        Edge(from_node=2, to_node=3, weight=20),
        Edge(from_node=3, to_node=0, weight=25),
        Edge(from_node=0, to_node=2, weight=30),
        Edge(from_node=1, to_node=3, weight=35)
    ]
    return Graph(nodes=nodes, edges=edges)

def test_chromosome_fitness_calculation(sample_graph):
    """
    Тест для перевірки обчислення придатності хромосоми.
    """
    # Створюємо валідний шлях
    valid_path = [0, 1, 2, 3]
    chromosome = Chromosome(valid_path, sample_graph)
    
    # Перевіряємо обчислення придатності
    expected_distance = 10 + 15 + 20 + 25  # Сума ваг ребер у шляху
    expected_fitness = 1.0 / expected_distance
    assert abs(chromosome.fitness - expected_fitness) < 1e-10
    
    # Перевіряємо невалідний шлях
    invalid_path = [0, 2, 1, 3]  # Шлях, де немає прямого з'єднання 2->1
    invalid_chromosome = Chromosome(invalid_path, sample_graph)
    assert invalid_chromosome.fitness == float('inf')

def test_genetic_algorithm_initialization(sample_graph):
    """
    Тест для перевірки ініціалізації генетичного алгоритму.
    """
    algorithm = GeneticAlgorithm(
        graph=sample_graph,
        population_size=100,
        mutation_rate=0.1,
        elite_size=10,
        max_generations=1000
    )
    
    # Перевіряємо початкову популяцію
    population = algorithm.initialize_population()
    assert len(population) == 100
    assert all(isinstance(chrom, Chromosome) for chrom in population)
    assert all(len(chrom.path) == len(sample_graph.nodes) for chrom in population)
    assert all(set(chrom.path) == set(sample_graph.nodes) for chrom in population)

def test_parent_selection(sample_graph):
    """
    Тест для перевірки вибору батьків.
    """
    algorithm = GeneticAlgorithm(sample_graph)
    population = algorithm.initialize_population()
    
    # Перевіряємо вибір батьків
    parent1, parent2 = algorithm.select_parents(population)
    assert isinstance(parent1, Chromosome)
    assert isinstance(parent2, Chromosome)
    assert parent1 != parent2  # Батьки повинні бути різними

def test_offspring_creation(sample_graph):
    """
    Тест для перевірки створення нащадків.
    """
    algorithm = GeneticAlgorithm(sample_graph)
    population = algorithm.initialize_population()
    parent1, parent2 = algorithm.select_parents(population)
    
    # Перевіряємо створення нащадків
    child1, child2 = algorithm.create_offspring(parent1, parent2)
    assert isinstance(child1, Chromosome)
    assert isinstance(child2, Chromosome)
    assert len(child1.path) == len(sample_graph.nodes)
    assert len(child2.path) == len(sample_graph.nodes)
    assert set(child1.path) == set(sample_graph.nodes)
    assert set(child2.path) == set(sample_graph.nodes)

def test_next_population_selection(sample_graph):
    """
    Тест для перевірки вибору наступної популяції.
    """
    algorithm = GeneticAlgorithm(sample_graph)
    current_population = algorithm.initialize_population()
    offspring = [algorithm.create_offspring(
        algorithm.select_parents(current_population)[0],
        algorithm.select_parents(current_population)[1]
    )[0] for _ in range(10)]
    
    # Перевіряємо вибір наступної популяції
    next_population = algorithm.select_next_population(current_population[:5], offspring)
    assert len(next_population) == algorithm.population_size
    assert all(isinstance(chrom, Chromosome) for chrom in next_population)
    assert all(len(chrom.path) == len(sample_graph.nodes) for chrom in next_population)

def test_stop_condition(sample_graph):
    """
    Тест для перевірки умови зупинки.
    """
    algorithm = GeneticAlgorithm(
        graph=sample_graph,
        max_generations=10,
        fitness_threshold=0.001
    )
    
    # Перевіряємо умову зупинки за кількістю поколінь
    algorithm.current_generation = 10
    assert algorithm.check_stop_condition(0.5) is True
    
    # Перевіряємо умову зупинки за зміною придатності
    algorithm.current_generation = 5
    algorithm.previous_best_fitness = 0.5
    assert algorithm.check_stop_condition(0.501) is False  # Зміна більша за поріг
    assert algorithm.check_stop_condition(0.5001) is True  # Зміна менша за поріг

@pytest.mark.asyncio
async def test_full_evolution_cycle(sample_graph):
    """
    Тест для перевірки повного циклу еволюції.
    """
    algorithm = GeneticAlgorithm(
        graph=sample_graph,
        population_size=50,
        max_generations=10
    )
    
    # Запускаємо еволюцію
    best_solution, generations, stats = await algorithm.evolve("test_run_id")
    
    # Перевіряємо результати
    assert best_solution is not None
    assert isinstance(best_solution, Chromosome)
    assert len(generations) <= 10  # Максимальна кількість поколінь
    assert all(gen.generation_number < 10 for gen in generations)
    assert all(gen.best_fitness > 0 for gen in generations)
    assert all(gen.average_fitness > 0 for gen in generations) 