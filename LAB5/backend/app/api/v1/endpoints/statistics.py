from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.models.evolution_stats import EvolutionStats
from app.models.generation import Generation
from app.crud.evolution_stats import get_evolution_stats, get_all_stats
from app.crud.generation import get_generations, get_latest_generation
from app.crud.algorithm_run import get_algorithm_run

router = APIRouter()

@router.get("/runs/{run_id}/generations", response_model=List[Generation])
async def read_run_generations(
    run_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """
    Отримання списку поколінь для конкретного запуску алгоритму.
    """
    # Перевіряємо чи існує запуск
    if not await get_algorithm_run(run_id):
        raise HTTPException(
            status_code=404,
            detail=f"Запуск з ID {run_id} не знайдено"
        )
    
    return await get_generations(
        run_id=run_id,
        skip=skip,
        limit=limit
    )

@router.get("/runs/{run_id}/generations/latest", response_model=Generation)
async def read_latest_generation(run_id: str):
    """
    Отримання останнього покоління для конкретного запуску алгоритму.
    """
    # Перевіряємо чи існує запуск
    if not await get_algorithm_run(run_id):
        raise HTTPException(
            status_code=404,
            detail=f"Запуск з ID {run_id} не знайдено"
        )
    
    generation = await get_latest_generation(run_id)
    if not generation:
        raise HTTPException(
            status_code=404,
            detail=f"Покоління для запуску з ID {run_id} не знайдено"
        )
    return generation

@router.get("/runs/{run_id}/stats", response_model=EvolutionStats)
async def read_run_evolution_stats(run_id: str):
    """
    Отримання статистики еволюції для конкретного запуску алгоритму.
    """
    # Перевіряємо чи існує запуск
    if not await get_algorithm_run(run_id):
        raise HTTPException(
            status_code=404,
            detail=f"Запуск з ID {run_id} не знайдено"
        )
    
    stats = await get_evolution_stats(run_id)
    if not stats:
        raise HTTPException(
            status_code=404,
            detail=f"Статистика для запуску з ID {run_id} не знайдена"
        )
    return stats

@router.get("/stats", response_model=List[EvolutionStats])
async def read_all_evolution_stats(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """
    Отримання списку всієї статистики еволюції.
    """
    return await get_all_stats(skip=skip, limit=limit) 