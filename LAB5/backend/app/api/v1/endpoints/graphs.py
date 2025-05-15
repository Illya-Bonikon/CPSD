from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.models.graph import Graph, GraphCreate, GraphUpdate
from app.crud.graph import (
    create_graph,
    get_graphs,
    get_graph,
    update_graph,
    delete_graph
)
from app.validators.graph import (
    validate_graph,
    GraphValidationError,
    GraphNotConnectedError,
    InvalidEdgeWeightError,
    DuplicateEdgeError,
    InvalidNodeError
)

router = APIRouter()

@router.post("/", response_model=Graph, status_code=201)
async def create_graph_endpoint(graph: GraphCreate):
    """
    Створення нового графа.
    """
    try:
        # Валідація графа
        validate_graph(graph)
        
        # Перевірка на дублікат назви
        existing_graphs = await get_graphs(name=graph.name)
        if existing_graphs:
            raise HTTPException(
                status_code=400,
                detail=f"Граф з назвою '{graph.name}' вже існує"
            )
        
        return await create_graph(graph)
    except GraphValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Помилка при створенні графа: {str(e)}"
        )

@router.get("/", response_model=List[Graph])
async def read_graphs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    name: Optional[str] = None
):
    """
    Отримання списку графів з фільтрацією та пагінацією.
    """
    try:
        return await get_graphs(skip=skip, limit=limit, name=name)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Помилка при отриманні списку графів: {str(e)}"
        )

@router.get("/{graph_id}", response_model=Graph)
async def read_graph(graph_id: str):
    """
    Отримання інформації про конкретний граф.
    """
    try:
        graph = await get_graph(graph_id)
        if not graph:
            raise HTTPException(
                status_code=404,
                detail=f"Граф з ID {graph_id} не знайдено"
            )
        return graph
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Помилка при отриманні графа: {str(e)}"
        )

@router.put("/{graph_id}", response_model=Graph)
async def update_graph_endpoint(graph_id: str, graph: GraphCreate):
    """
    Оновлення існуючого графа.
    """
    try:
        # Валідація графа
        validate_graph(graph)
        
        # Перевірка існування графа
        existing_graph = await get_graph(graph_id)
        if not existing_graph:
            raise HTTPException(
                status_code=404,
                detail=f"Граф з ID {graph_id} не знайдено"
            )
        
        # Перевірка на дублікат назви
        if graph.name != existing_graph.name:
            graphs_with_name = await get_graphs(name=graph.name)
            if graphs_with_name:
                raise HTTPException(
                    status_code=400,
                    detail=f"Граф з назвою '{graph.name}' вже існує"
                )
        
        updated_graph = await update_graph(graph_id, graph)
        if not updated_graph:
            raise HTTPException(
                status_code=400,
                detail="Не вдалося оновити граф"
            )
        return updated_graph
    except GraphValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Помилка при оновленні графа: {str(e)}"
        )

@router.delete("/{graph_id}", status_code=204)
async def delete_graph_endpoint(graph_id: str):
    """
    Видалення графа.
    """
    try:
        # Перевірка існування графа
        graph = await get_graph(graph_id)
        if not graph:
            raise HTTPException(
                status_code=404,
                detail=f"Граф з ID {graph_id} не знайдено"
            )
        
        if not await delete_graph(graph_id):
            raise HTTPException(
                status_code=400,
                detail="Не вдалося видалити граф"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Помилка при видаленні графа: {str(e)}"
        ) 