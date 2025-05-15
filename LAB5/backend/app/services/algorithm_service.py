from typing import Optional
from app.models.graph import Graph
from app.models.algorithm_run import AlgorithmRun
from app.crud.graph import get_graph
from app.crud.algorithm_run import get_algorithm_run, update_algorithm_run_status
from app.algorithms.genetic import GeneticAlgorithm

async def check_run_status(run_id: str) -> bool:
    """
    Перевірка статусу виконання алгоритму.
    """
    run = await get_algorithm_run(run_id)
    return run is not None and run.status == "running"

async def run_genetic_algorithm(run_id: str) -> Optional[AlgorithmRun]:
    """
    Запуск генетичного алгоритму для пошуку найкоротшого шляху.
    """
    # Отримуємо інформацію про запуск
    run = await get_algorithm_run(run_id)
    if not run:
        return None
    
    # Отримуємо граф
    graph = await get_graph(str(run.graph_id))
    if not graph:
        await update_algorithm_run_status(
            run_id,
            {"status": "failed", "error": "Граф не знайдено"}
        )
        return None
    
    try:
        # Створюємо екземпляр генетичного алгоритму
        algorithm = GeneticAlgorithm(
            graph=graph,
            population_size=100,
            mutation_rate=0.1,
            elite_size=10,
            max_generations=1000
        )
        
        # Запускаємо еволюцію
        best_solution, generations, stats = await algorithm.evolve(
            run_id,
            check_status_callback=check_run_status
        )
        
        # Оновлюємо статус виконання
        await update_algorithm_run_status(
            run_id,
            {
                "status": "completed",
                "current_generation": algorithm.current_generation,
                "best_path": best_solution.path,
                "best_fitness": best_solution.fitness
            }
        )
        
        return await get_algorithm_run(run_id)
    
    except Exception as e:
        # У разі помилки оновлюємо статус
        await update_algorithm_run_status(
            run_id,
            {
                "status": "failed",
                "error": str(e)
            }
        )
        return None 