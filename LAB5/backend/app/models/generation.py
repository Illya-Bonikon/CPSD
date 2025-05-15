from typing import List, Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import datetime
from .common import MongoId

class PathSolution(BaseModel):
    path: List[int]
    distance: float
    fitness: float

class GenerationStatistics(BaseModel):
    best_distance: float
    average_distance: float
    worst_distance: float
    best_path: List[int]
    diversity: float

class GenerationBase(BaseModel):
    run_id: MongoId
    generation_number: int = Field(..., ge=0)
    population: List[List[int]] = Field(..., min_items=1)
    fitness_values: List[float] = Field(..., min_items=1)
    best_path: List[int]
    best_fitness: float
    average_fitness: float
    worst_fitness: float

class GenerationCreate(GenerationBase):
    pass

class Generation(GenerationBase):
    id: MongoId = Field(alias="_id")
    created_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {
            MongoId: str,
            datetime: lambda dt: dt.isoformat()
        }

class GenerationInDB(Generation):
    pass 