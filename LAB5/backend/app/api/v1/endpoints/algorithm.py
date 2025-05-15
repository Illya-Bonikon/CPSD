from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from app.models.algorithm_run import AlgorithmRun, AlgorithmRunCreate
from app.crud.algorithm_run import (
    create_algorithm_run,
    get_algorithm_runs,
    get_algorithm_run,
    delete_algorithm_run,
    update_algorithm_run_status
)
from app.crud.graph import get_graph
from app.crud import generation as generation_crud
from app.crud import evolution_stats as stats_crud
from app.services.algorithm_service import run_genetic_algorithm
from app.validators.algorithm import (
    validate_algorithm_parameters,
    AlgorithmValidationError
)

router = APIRouter()

@router.post("/runs", response_model=AlgorithmRun, status_code=201)
async def create_algorithm_run_endpoint(
    run: AlgorithmRunCreate,
    background_tasks: BackgroundTasks
):
    """
    Створення нового запуску алгоритму.
    """
    try:
        # Перевіряємо чи існує граф
        graph = await get_graph(str(run.graph_id))
        if not graph:
            raise HTTPException(
                status_code=404,
                detail=f"Граф з ID {run.graph_id} не знайдено"
            )
        
        # Перевіряємо чи немає вже запущених алгоритмів для цього графа
        running_runs = await get_algorithm_runs(graph_id=str(run.graph_id), status="running")
        if running_runs:
            raise HTTPException(
                status_code=400,
                detail="Для цього графа вже є запущений алгоритм"
            )
        
        # Валідуємо параметри алгоритму
        try:
            algorithm_params = validate_algorithm_parameters(
                population_size=run.population_size,
                mutation_rate=run.mutation_rate,
                elite_size=run.elite_size,
                max_generations=run.max_generations,
                fitness_threshold=run.fitness_threshold
            )
            # Оновлюємо параметри запуску валідними значеннями
            run.population_size = algorithm_params.population_size
            run.mutation_rate = algorithm_params.mutation_rate
            run.elite_size = algorithm_params.elite_size
            run.max_generations = algorithm_params.max_generations
            run.fitness_threshold = algorithm_params.fitness_threshold
        except AlgorithmValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Створюємо запис про запуск
        algorithm_run = await create_algorithm_run(run)
        
        # Запускаємо алгоритм у фоновому режимі
        background_tasks.add_task(run_genetic_algorithm, str(algorithm_run.id))
        
        return algorithm_run
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Помилка при створенні запуску алгоритму: {str(e)}"
        )

@router.get("/runs", response_model=List[AlgorithmRun])
async def read_algorithm_runs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    graph_id: Optional[str] = None,
    status: Optional[str] = None
):
    """
    Отримання списку запусків алгоритму з фільтрацією та пагінацією.
    """
    try:
        return await get_algorithm_runs(
            skip=skip,
            limit=limit,
            graph_id=graph_id,
            status=status
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Помилка при отриманні списку запусків: {str(e)}"
        )

@router.get("/runs/{run_id}", response_model=AlgorithmRun)
async def read_algorithm_run(run_id: str):
    """
    Отримання інформації про конкретний запуск алгоритму.
    """
    try:
        run = await get_algorithm_run(run_id)
        if not run:
            raise HTTPException(
                status_code=404,
                detail=f"Запуск з ID {run_id} не знайдено"
            )
        return run
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Помилка при отриманні запуску: {str(e)}"
        )

@router.delete("/runs/{run_id}", status_code=204)
async def delete_algorithm_run_endpoint(run_id: str):
    """
    Видалення запуску алгоритму та всіх пов'язаних даних.
    """
    try:
        # Перевіряємо чи існує запуск
        run = await get_algorithm_run(run_id)
        if not run:
            raise HTTPException(
                status_code=404,
                detail=f"Запуск з ID {run_id} не знайдено"
            )
        
        # Видаляємо всі пов'язані дані
        await generation_crud.delete_run_generations(run_id)
        await stats_crud.delete_run_evolution_stats(run_id)
        
        # Видаляємо сам запуск
        if not await delete_algorithm_run(run_id):
            raise HTTPException(
                status_code=400,
                detail="Не вдалося видалити запуск алгоритму"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Помилка при видаленні запуску: {str(e)}"
        )

@router.post("/runs/{run_id}/pause", response_model=AlgorithmRun)
async def pause_algorithm_run(run_id: str):
    """
    Призупинення виконання алгоритму.
    """
    try:
        run = await get_algorithm_run(run_id)
        if not run:
            raise HTTPException(
                status_code=404,
                detail=f"Запуск з ID {run_id} не знайдено"
            )
        
        if run.status != "running":
            raise HTTPException(
                status_code=400,
                detail="Можна призупинити тільки запущений алгоритм"
            )
        
        updated_run = await update_algorithm_run_status(
            run_id,
            {"status": "paused"}
        )
        if not updated_run:
            raise HTTPException(
                status_code=400,
                detail="Не вдалося призупинити алгоритм"
            )
        return updated_run
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Помилка при призупиненні алгоритму: {str(e)}"
        )

@router.post("/runs/{run_id}/resume", response_model=AlgorithmRun)
async def resume_algorithm_run(run_id: str):
    """
    Відновлення виконання алгоритму.
    """
    try:
        run = await get_algorithm_run(run_id)
        if not run:
            raise HTTPException(
                status_code=404,
                detail=f"Запуск з ID {run_id} не знайдено"
            )
        
        if run.status != "paused":
            raise HTTPException(
                status_code=400,
                detail="Можна відновити тільки призупинений алгоритм"
            )
        
        updated_run = await update_algorithm_run_status(
            run_id,
            {"status": "running"}
        )
        if not updated_run:
            raise HTTPException(
                status_code=400,
                detail="Не вдалося відновити алгоритм"
            )
        return updated_run
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Помилка при відновленні алгоритму: {str(e)}"
        ) 