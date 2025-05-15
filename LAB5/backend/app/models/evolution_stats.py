from typing import List, Optional
from pydantic import BaseModel, Field
from .common import MongoId
from datetime import datetime

class GenerationStat(BaseModel):
    generation: int
    best_distance: float
    average_distance: float
    worst_distance: float
    diversity: float

class EvolutionStatsBase(BaseModel):
    run_id: MongoId
    generations_count: int = Field(..., gt=0)
    best_fitness_history: List[float] = Field(..., min_items=1)
    average_fitness_history: List[float] = Field(..., min_items=1)
    worst_fitness_history: List[float] = Field(..., min_items=1)
    convergence_generation: Optional[int] = None
    improvement_rate: float = Field(..., ge=0)
    diversity_history: List[float] = Field(..., min_items=1)

class EvolutionStatsCreate(EvolutionStatsBase):
    pass

class EvolutionStats(EvolutionStatsBase):
    id: MongoId = Field(alias="_id")
    created_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {
            MongoId: str,
            datetime: lambda dt: dt.isoformat()
        }

class EvolutionStatsInDB(EvolutionStats):
    pass 