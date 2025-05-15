from typing import List, Tuple, Optional
import random
import numpy as np
from app.models.graph import Graph
from app.models.generation import Generation, GenerationCreate
from app.models.evolution_stats import EvolutionStats, EvolutionStatsCreate
from app.crud.generation import create_generation
from app.crud.evolution_stats import create_evolution_stats, update_evolution_stats, get_evolution_stats
from app.crud.algorithm_run import update_algorithm_run_status

class Chromosome:
    def __init__(self, path: List[int], graph: Graph):
        self.path = path
        self.graph = graph
        self._fitness: Optional[float] = None
    
    @property
    def fitness(self) -> float:
        """
        (2) Оцінка придатності 
        Обчислення значення придатності для особини на основі довжини шляху.
        """
        if self._fitness is None:
            self._fitness = self._calculate_fitness()
        return self._fitness
    
    def _calculate_fitness(self) -> float:
        total_distance = self._calculate_path_distance()
        return 1.0 / total_distance if total_distance > 0 else float('inf')
    
    def _calculate_path_distance(self) -> float:
        total_distance = 0
        
        for i in range(len(self.path) - 1):
            edge_distance = self._get_edge_distance(self.path[i], self.path[i + 1])
            if edge_distance == float('inf'):
                return float('inf')
            total_distance += edge_distance
        
        last_edge_distance = self._get_edge_distance(self.path[-1], self.path[0])
        if last_edge_distance == float('inf'):
            return float('inf')
        
        return total_distance + last_edge_distance
    
    def _get_edge_distance(self, from_node: int, to_node: int) -> float:
        edge = next(
            (e for e in self.graph.edges if e.from_node == from_node and e.to_node == to_node),
            None
        )
        return edge.weight if edge else float('inf')

class GeneticAlgorithm:
    def __init__(
        self,
        graph: Graph,
        population_size: int = 100,
        mutation_rate: float = 0.1,
        elite_size: int = 10,
        max_generations: int = 1000,
        fitness_threshold: float = 0.001
    ):
        self.graph = graph
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size
        self.max_generations = max_generations
        self.fitness_threshold = fitness_threshold
        self.nodes = list(range(len(graph.nodes)))
        self.best_solution: Optional[Chromosome] = None
        self.current_generation = 0
        self.previous_best_fitness: Optional[float] = None
    
    def initialize_population(self) -> List[Chromosome]:
        """
        (1) Ініціалізація популяції\
        """
        population = []
        for _ in range(self.population_size):
            path = self._create_random_path()
            population.append(Chromosome(path, self.graph))
        return population
    
    def _create_random_path(self) -> List[int]:
        path = self.nodes.copy()
        random.shuffle(path)
        return path
    
    def evaluate_population_fitness(self, population: List[Chromosome]) -> None:
        """
        (2, 5) Оцінка придатності
        Обчислення значень придатності для кожної особини.
        """
        for chromosome in population:
            _ = chromosome.fitness  
    
    def select_parents(self, population: List[Chromosome]) -> Tuple[Chromosome, Chromosome]:
        """
        (3) Вибір батьків
        """
        parent1 = self._tournament_selection(population)
        parent2 = self._tournament_selection(population)
        return parent1, parent2
    
    def _tournament_selection(self, population: List[Chromosome], tournament_size: int = 5) -> Chromosome:

        tournament = random.sample(population, tournament_size)
        return max(tournament, key=lambda x: x.fitness)
    
    def create_offspring(self, parent1: Chromosome, parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        """
        (4) Створення нащадків
        """
        child1, child2 = self._crossover(parent1, parent2)
        child1 = self._mutate(child1)
        child2 = self._mutate(child2)
        return child1, child2
    
    def _crossover(self, parent1: Chromosome, parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:

        size = len(parent1.path)
        point = random.randint(0, size - 1)
        
        child1_path = self._create_child_path(parent1.path, parent2.path, point)
        child2_path = self._create_child_path(parent2.path, parent1.path, point)
        
        return (
            Chromosome(child1_path, self.graph),
            Chromosome(child2_path, self.graph)
        )
    
    def _create_child_path(self, parent1_path: List[int], parent2_path: List[int], point: int) -> List[int]:

        size = len(parent1_path)
        child_path = [-1] * size
        
        child_path[:point] = parent1_path[:point]
        
        for i in range(size):
            if child_path[i] == -1:
                for gene in parent2_path:
                    if gene not in child_path:
                        child_path[i] = gene
                        break
        
        return child_path
    
    def _mutate(self, chromosome: Chromosome) -> Chromosome:

        if random.random() < self.mutation_rate:
            path = chromosome.path.copy()
            i, j = random.sample(range(len(path)), 2)
            path[i], path[j] = path[j], path[i]
            return Chromosome(path, self.graph)
        return chromosome
    
    def select_next_population(self, current_population: List[Chromosome], offspring: List[Chromosome]) -> List[Chromosome]:
        """
        (6) Вибір для наступної популяції
        """
        all_individuals = current_population + offspring
        all_individuals.sort(key=lambda x: x.fitness, reverse=True)

        return all_individuals[:self.population_size]
    
    def check_stop_condition(self, current_best_fitness: float) -> bool:
        """
        (7) Перевірка умови зупинки
        Перевірка чи досягнуто умову зупинки.
        """
        if self.current_generation >= self.max_generations:
            return True
        
        if self.previous_best_fitness is not None:
            fitness_change = abs(current_best_fitness - self.previous_best_fitness)
            if fitness_change < self.fitness_threshold:
                return True
        
        self.previous_best_fitness = current_best_fitness
        return False
    
    def get_best_solution(self) -> Optional[Chromosome]:
        """
        (8) Вивід результатів
        """
        return self.best_solution
    
    async def evolve(
        self,
        run_id: str,
        check_status_callback=None
    ) -> Tuple[Chromosome, List[Generation], EvolutionStats]:
        """
        Основний цикл еволюції. (3-7)
        """
        # (1) Ініціалізація популяції
        population = self.initialize_population()
        generations_data = []
        best_fitness_history = []
        avg_fitness_history = []
        
        for generation in range(self.max_generations):
            self.current_generation = generation
            
            if check_status_callback and not await check_status_callback(run_id):
                break
            
            # (2) Оцінка придатності
            self.evaluate_population_fitness(population)
            population.sort(key=lambda x: x.fitness, reverse=True)
            
            if self.best_solution is None or population[0].fitness > self.best_solution.fitness:
                self.best_solution = population[0]
            
            best_fitness = population[0].fitness
            avg_fitness = sum(chrom.fitness for chrom in population) / len(population)
            best_fitness_history.append(best_fitness)
            avg_fitness_history.append(avg_fitness)
            
            # (3-4) Створення нової популяції
            offspring = []
            while len(offspring) < self.population_size - self.elite_size:
                parent1, parent2 = self.select_parents(population)

                child1, child2 = self.create_offspring(parent1, parent2)
                offspring.extend([child1, child2])
            
            # (5) Оцінка придатності нової популяції
            self.evaluate_population_fitness(offspring)
            
            # (6) Вибір для наступної популяції
            population = self.select_next_population(population[:self.elite_size], offspring)
            
            generation_data = GenerationCreate(
                run_id=run_id,
                generation_number=generation,
                best_fitness=best_fitness,
                average_fitness=avg_fitness,
                best_path=population[0].path
            )
            created_generation = await create_generation(generation_data)
            generations_data.append(created_generation)
            
            stats_data = EvolutionStatsCreate(
                run_id=run_id,
                best_fitness_history=best_fitness_history,
                average_fitness_history=avg_fitness_history,
                best_path=self.best_solution.path,
                current_generation=generation
            )
            
            if generation == 0:
                await create_evolution_stats(stats_data)
            else:
                await update_evolution_stats(run_id, stats_data.model_dump())
            
            # (7) Перевірка умови зупинки
            if self.check_stop_condition(best_fitness):
                break
        
        await update_algorithm_run_status(
            run_id,
            {
                "status": "completed",
                "current_generation": self.current_generation
            }
        )
        
		# (8) Вивід результатів
        return self.best_solution, generations_data, await get_evolution_stats(run_id) 