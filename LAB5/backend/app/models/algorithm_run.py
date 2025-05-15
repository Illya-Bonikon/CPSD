from typing import List, Optional
from pydantic import BaseModel, Field, validator
from bson import ObjectId
from datetime import datetime
from .common import MongoId

class AlgorithmParameters(BaseModel):
    population_size: int = Field(..., gt=0)
    generations: int = Field(..., gt=0)
    mutation_rate: float = Field(..., ge=0, le=1)
    crossover_rate: float = Field(..., ge=0, le=1)
    tournament_size: int = Field(..., gt=1)
    elite_size: int = Field(..., ge=0)
    parallel_workers: int = Field(..., gt=0)

    @validator('elite_size')
    def validate_elite_size(cls, v, values):
        if 'population_size' in values and v >= values['population_size']:
            raise ValueError("elite_size must be less than population_size")
        return v

    @validator('tournament_size')
    def validate_tournament_size(cls, v, values):
        if 'population_size' in values and v > values['population_size']:
            raise ValueError("tournament_size must not exceed population_size")
        return v

class AlgorithmRunBase(BaseModel):
    graph_id: MongoId
    population_size: int = Field(..., gt=0)
    mutation_rate: float = Field(..., ge=0, le=1)
    crossover_rate: float = Field(..., ge=0, le=1)
    generations: int = Field(..., gt=0)
    elite_size: int = Field(..., ge=0)
    tournament_size: int = Field(..., gt=0)

class AlgorithmRunCreate(AlgorithmRunBase):
    pass

class AlgorithmRun(AlgorithmRunBase):
    id: MongoId = Field(alias="_id")
    status: str = Field(..., pattern="^(running|paused|completed|failed)$")
    start_time: datetime
    end_time: Optional[datetime] = None
    best_path: Optional[list[int]] = None
    best_fitness: Optional[float] = None
    current_generation: int = Field(0, ge=0)

    class Config:
        populate_by_name = True
        json_encoders = {
            MongoId: str,
            datetime: lambda dt: dt.isoformat()
        }

class AlgorithmRunInDB(AlgorithmRun):
    pass 