import os
from pathlib import Path
from typing import Dict, Any

# Базові шляхи
BASE_DIR: Path = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR: Path = BASE_DIR / 'data'
MODELS_DIR: Path = BASE_DIR / 'models'
LOGS_DIR: Path = BASE_DIR / 'logs'

# Створюємо необхідні директорії
for directory in [DATA_DIR, MODELS_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# Конфігурація бази даних
DB_CONFIG: Dict[str, Any] = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'database': os.getenv('DB_NAME', 'weather_prediction'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'SQL55455445kjk.SQL'),
}

# Конфігурація моделі
MODEL_CONFIG: Dict[str, Any] = {
    'model_path': str(MODELS_DIR / 'temperature_lstm.keras'),
    'data_path': str(DATA_DIR / 'weather_data.csv'),
    'sequence_length': int(os.getenv('SEQUENCE_LENGTH', '365')),  # Довжина послідовності для навчання
    'batch_size': int(os.getenv('BATCH_SIZE', '64')),  # Розмір батчу
    'epochs': int(os.getenv('EPOCHS', '50')),  # Кількість епох
    'learning_rate': float(os.getenv('LEARNING_RATE', '0.001')),  # Швидкість навчання
    'validation_split': float(os.getenv('VALIDATION_SPLIT', '0.2')),  # Частка валідаційних даних
    'early_stopping_patience': int(os.getenv('EARLY_STOPPING_PATIENCE', '10')),  # Терпіння для раннього зупинки
    'reduce_lr_patience': int(os.getenv('REDUCE_LR_PATIENCE', '5')),  # Терпіння для зменшення швидкості навчання
}

# Конфігурація додатку
APP_CONFIG: Dict[str, Any] = {
    'debug': os.getenv('DEBUG', 'True').lower() == 'true',
    'log_level': os.getenv('LOG_LEVEL', 'INFO'),
    'log_file': str(LOGS_DIR / 'app.log'),
}

# Експорт констант для зворотної сумісності
DB_HOST = DB_CONFIG['host']
DB_PORT = DB_CONFIG['port']
DB_NAME = DB_CONFIG['database']
DB_USER = DB_CONFIG['user']
DB_PASSWORD = DB_CONFIG['password']

MODEL_PATH = MODEL_CONFIG['model_path']
CSV_DATA_PATH = MODEL_CONFIG['data_path']
SEQUENCE_LENGTH = MODEL_CONFIG['sequence_length']
BATCH_SIZE = MODEL_CONFIG['batch_size']
EPOCHS = MODEL_CONFIG['epochs']

DEBUG = APP_CONFIG['debug']
LOG_LEVEL = APP_CONFIG['log_level'] 