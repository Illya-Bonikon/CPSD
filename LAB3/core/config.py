from dataclasses import dataclass
from typing import Optional
from pathlib import Path
from .constants import *

@dataclass
class DatabaseConfig:
    host: str = DB_HOST
    port: int = DB_PORT
    name: str = DB_NAME
    user: str = DB_USER
    password: str = DB_PASSWORD
    
    def get_connection_string(self) -> str:
        return f"mysql+mysqlconnector://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

@dataclass
class ModelConfig:
    model_path: Path = Path(MODEL_PATH)
    data_path: Path = Path(CSV_DATA_PATH)
    sequence_length: int = SEQUENCE_LENGTH
    batch_size: int = BATCH_SIZE
    epochs: int = EPOCHS
    learning_rate: float = 0.001
    validation_split: float = 0.2
    early_stopping_patience: int = 10
    reduce_lr_patience: int = 5
    
    def __post_init__(self):
        self.model_path = Path(self.model_path)
        self.data_path = Path(self.data_path)
        if not self.model_path.parent.exists():
            self.model_path.parent.mkdir(parents=True)

@dataclass
class AppConfig:
    debug: bool = DEBUG
    log_level: str = LOG_LEVEL
    log_file: Optional[Path] = None
    
    def __post_init__(self):
        if self.log_file:
            self.log_file = Path(self.log_file)
            if not self.log_file.parent.exists():
                self.log_file.parent.mkdir(parents=True)

class Config:
    def __init__(self):
        self.db = DatabaseConfig()
        self.model = ModelConfig()
        self.app = AppConfig()
        
    def validate(self) -> bool:
        """Валідація конфігурації"""
        try:
            # Перевірка бази даних
            if not all([self.db.host, self.db.port, self.db.name, self.db.user, self.db.password]):
                raise ValueError("Відсутні необхідні параметри підключення до бази даних")
                
            # Перевірка моделі
            if not self.model.data_path.exists():
                raise ValueError(f"Файл з даними не знайдено: {self.model.data_path}")
                
            if self.model.sequence_length <= 0:
                raise ValueError("sequence_length повинен бути більше 0")
                
            if self.model.batch_size <= 0:
                raise ValueError("batch_size повинен бути більше 0")
                
            if self.model.epochs <= 0:
                raise ValueError("epochs повинен бути більше 0")
                
            if not 0 < self.model.validation_split < 1:
                raise ValueError("validation_split повинен бути між 0 та 1")
                
            # Перевірка додатку
            if self.app.log_file and not self.app.log_file.parent.exists():
                raise ValueError(f"Директорія для лог-файлу не існує: {self.app.log_file.parent}")
                
            return True
            
        except Exception as e:
            print(f"Помилка валідації конфігурації: {e}")
            return False 