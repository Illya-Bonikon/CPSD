from typing import Optional
from pydantic import BaseModel, Field, validator

class AlgorithmValidationError(Exception):
    """Базовий клас для помилок валідації параметрів алгоритму"""
    pass

class AlgorithmParameters(BaseModel):
    """
    Модель параметрів генетичного алгоритму з валідацією.
    """
    population_size: int = Field(
        default=100,
        ge=10,
        le=1000,
        description="Розмір популяції"
    )
    mutation_rate: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Ймовірність мутації"
    )
    elite_size: int = Field(
        default=10,
        ge=1,
        description="Кількість елітних особин"
    )
    max_generations: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Максимальна кількість поколінь"
    )
    fitness_threshold: float = Field(
        default=0.001,
        ge=0.0,
        le=1.0,
        description="Поріг зміни придатності для зупинки"
    )
    
    @validator('elite_size')
    def validate_elite_size(cls, v, values):
        """
        Перевірка, що розмір еліти не перевищує розмір популяції.
        """
        if 'population_size' in values and v > values['population_size']:
            raise AlgorithmValidationError(
                "Розмір еліти не може бути більшим за розмір популяції"
            )
        return v
    
    @validator('elite_size')
    def validate_elite_size_minimum(cls, v, values):
        """
        Перевірка, що розмір еліти не менший за мінімальне значення.
        """
        if 'population_size' in values and v < values['population_size'] * 0.01:
            raise AlgorithmValidationError(
                "Розмір еліти повинен бути не меншим за 1% від розміру популяції"
            )
        return v
    
    @validator('mutation_rate')
    def validate_mutation_rate(cls, v):
        """
        Перевірка, що ймовірність мутації знаходиться в розумних межах.
        """
        if v < 0.01:
            raise AlgorithmValidationError(
                "Ймовірність мутації повинна бути не меншою за 1%"
            )
        if v > 0.5:
            raise AlgorithmValidationError(
                "Ймовірність мутації повинна бути не більшою за 50%"
            )
        return v
    
    @validator('population_size')
    def validate_population_size(cls, v):
        """
        Перевірка, що розмір популяції є парним числом.
        """
        if v % 2 != 0:
            raise AlgorithmValidationError(
                "Розмір популяції повинен бути парним числом"
            )
        return v

def validate_algorithm_parameters(
    population_size: Optional[int] = None,
    mutation_rate: Optional[float] = None,
    elite_size: Optional[int] = None,
    max_generations: Optional[int] = None,
    fitness_threshold: Optional[float] = None
) -> AlgorithmParameters:
    """
    Валідація параметрів алгоритму.
    """
    try:
        return AlgorithmParameters(
            population_size=population_size,
            mutation_rate=mutation_rate,
            elite_size=elite_size,
            max_generations=max_generations,
            fitness_threshold=fitness_threshold
        )
    except Exception as e:
        raise AlgorithmValidationError(str(e)) 