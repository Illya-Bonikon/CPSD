from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from functools import lru_cache

class Settings(BaseSettings):
    # Базова конфігурація
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Genetic Algorithm API"
    
    # Налаштування CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # React dev server
        "http://127.0.0.1:3000",
    ]
    
    # Налаштування бази даних
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "genetic_algorithm_db"
    
    # Налаштування алгоритму
    DEFAULT_POPULATION_SIZE: int = 100
    DEFAULT_MUTATION_RATE: float = 0.1
    DEFAULT_ELITE_SIZE: int = 10
    DEFAULT_MAX_GENERATIONS: int = 1000
    DEFAULT_FITNESS_THRESHOLD: float = 0.001
    
    # Налаштування API
    API_DOCS_URL: str = "/docs"
    API_REDOC_URL: str = "/redoc"
    API_OPENAPI_URL: str = "/openapi.json"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings() 