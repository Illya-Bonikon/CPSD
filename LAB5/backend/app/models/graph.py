from typing import List, Optional
from pydantic import BaseModel, Field
from .common import MongoId
from datetime import datetime

class Edge(BaseModel):
    """Модель ребра графа"""
    from_node: int = Field(..., description="Початкова вершина")
    to_node: int = Field(..., description="Кінцева вершина")
    weight: float = Field(..., gt=0, description="Вага ребра")

class GraphBase(BaseModel):
    """Базова модель графа"""
    name: str = Field(..., min_length=1, max_length=100, description="Назва графа")
    nodes: List[int] = Field(..., description="Список вершин")
    edges: List[Edge] = Field(..., description="Список ребер")

class GraphCreate(GraphBase):
    """Модель для створення графа"""
    pass

class GraphUpdate(GraphBase):
    """Модель для оновлення графа"""
    pass

class Graph(GraphBase):
    """Повна модель графа з ID та датами"""
    id: str = Field(..., description="Унікальний ідентифікатор")
    created_at: datetime = Field(..., description="Дата створення")
    updated_at: datetime = Field(..., description="Дата останнього оновлення")

    class Config:
        from_attributes = True

class GraphInDB(Graph):
    pass 