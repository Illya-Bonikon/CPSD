import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass, field



load_dotenv() 

@dataclass
class DatabaseConfig:
    host: str = field(default_factory=lambda: os.getenv("DB_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("DB_PORT", "3306")))
    name: str = field(default_factory=lambda: os.getenv("DB_NAME", "weather_prediction"))
    user: str = field(default_factory=lambda: os.getenv("DB_USER", "root"))
    password: str = field(default_factory=lambda: os.getenv("DB_PASSWORD", ""))
    
    def get_connection_string(self) -> str:
        return f"mysql+mysqlconnector://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

@dataclass
class ModelConfig:
    model_path: Path = field(default_factory=lambda: Path(os.getenv("MODEL_PATH", "models/temperature_lstm.keras")))
    data_path: Path = field(default_factory=lambda: Path(os.getenv("DATA_PATH", "data/weather_data.csv")))
    sequence_length: int = field(default_factory=lambda: int(os.getenv("SEQUENCE_LENGTH", "30")))
    batch_size: int = field(default_factory=lambda: int(os.getenv("BATCH_SIZE", "64")))
    epochs: int = field(default_factory=lambda: int(os.getenv("EPOCHS", "50")))
    learning_rate: float = field(default_factory=lambda: float(os.getenv("LEARNING_RATE", "0.001")))
    validation_split: float = field(default_factory=lambda: float(os.getenv("VALIDATION_SPLIT", "0.2")))
    early_stopping_patience: int = field(default_factory=lambda: int(os.getenv("EARLY_STOPPING_PATIENCE", "10")))
    reduce_lr_patience: int = field(default_factory=lambda: int(os.getenv("REDUCE_LR_PATIENCE", "5")))
    
    def __post_init__(self):
        ensure_directory(self.model_path.parent)


@dataclass
class AppConfig:
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "True").lower() == "true")
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    log_file: Optional[Path] = field(default_factory=lambda: Path(os.getenv("LOG_FILE", "logs/app.log")))
    
    def __post_init__(self):
        ensure_directory(self.log_file.parent)

class Config:
    def __init__(self):
        self.db = DatabaseConfig()
        self.model = ModelConfig()
        self.app = AppConfig()
        
    def validate(self) -> bool:
        try:
            self._validate_db()
            self._validate_model()
            self._validate_app()
            return True
        except Exception as e:
            print(f"Помилка валідації конфігурації: {e}")
            return False

    def _validate_db(self):
        if not all([self.db.host, self.db.port, self.db.name, self.db.user, self.db.password]):
            raise ValueError("Відсутні необхідні параметри підключення до бази даних")

    def _validate_model(self):
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
        
    def _validate_app(self):
        if self.app.log_file and not self.app.log_file.parent.exists():
            raise ValueError(f"Директорія для лог-файлу не існує: {self.app.log_file.parent}")


def ensure_directory(path: Path):
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)