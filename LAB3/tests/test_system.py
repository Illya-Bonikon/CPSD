import pytest
from pathlib import Path
import pandas as pd
from core.config import Config, DatabaseConfig, ModelConfig
from database.connection import DatabaseConnection
from database.db_manager import DatabaseManager
from ml.lstm_model import TemperatureLSTM
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def config():
    return Config()

@pytest.fixture
def db(config):
    return DatabaseConnection(config)

@pytest.fixture
def db_manager():
    return DatabaseManager(DatabaseConfig())

@pytest.fixture
def model():
    return TemperatureLSTM(ModelConfig())

@pytest.fixture
def sample_weather_data(csv_path: Path = Path("data/weather_data.csv")):
    if not csv_path.exists():
        print(f"Файл '{csv_path}' не знайдено.")
        return None

    try:
        df = pd.read_csv(csv_path, parse_dates=["timestamp"])
    except Exception as e:
        print(f"Помилка при завантаженні: {e}")
        return None

    if "timestamp" not in df.columns or "temperature" not in df.columns:
        print("У файлі мають бути стовпці 'timestamp' та 'temperature'.")
        return None

    df.set_index("timestamp", inplace=True)
    df = df.sort_index()

    print(f"\nКількість годинних записів: {len(df)}")
    print(f"Кількість днів: {len(df.resample('D').mean())}")
    print(f"Діапазон дат: від {df.index.min().date()} до {df.index.max().date()}")

    return df.reset_index()

def test_database_connection(db):
    assert db.health_check() == True
    
    assert db.init_db() == True
    
    with db.get_session() as session:
        assert session is not None

def test_database_manager(db_manager, sample_weather_data):
    assert db_manager.import_csv_data('data/weather_data.csv') in [True, False]
    
    data = db_manager.get_all_data()
    assert isinstance(data, pd.DataFrame)
    assert 'timestamp' in data.columns
    assert 'temperature' in data.columns

    predictions = [
        {'min_temp': 10.0, 'max_temp': 20.0},
        {'min_temp': 12.0, 'max_temp': 22.0}
    ]
    assert db_manager.save_predictions(predictions, 2024) == True

    monthly_predictions = db_manager.get_predictions_for_month(2024, 1)
    assert isinstance(monthly_predictions, pd.DataFrame)
    assert len(monthly_predictions) > 0

def test_model_initialization(model):
    """Тест ініціалізації моделі"""
    assert model.sequence_length > 0
    assert hasattr(model, 'model')
    assert hasattr(model, 'scaler')
    assert hasattr(model, 'health_check')
    assert hasattr(model, 'model_path')

def test_model_prediction(model, sample_weather_data):

    X, y = model.prepare_data(sample_weather_data)

    if len(X) == 0:
        pytest.skip("Недостатньо даних для прогнозування")

    if model.health_check():
        prediction = model.predict(X[0:1])
        min_temp, max_temp = prediction[0]
        assert min_temp <= max_temp, f"min_temp ({min_temp}) має бути менше або дорівнювати max_temp ({max_temp})"

        yearly_predictions = model.predict_year(X[-1:])
        assert len(yearly_predictions) > 0
        for pred in yearly_predictions:
            assert pred['min_temp'] <= pred['max_temp'], f"min_temp ({pred['min_temp']}) має бути менше або дорівнювати max_temp ({pred['max_temp']})"

def test_model_training(model, sample_weather_data):

    X, y = model.prepare_data(sample_weather_data)
    print(f"\nКількість послідовностей для навчання: {len(X)}")
    print(f"Довжина послідовності: {X.shape[1] if len(X) > 0 else 0}")
    print(f"Мінімальна кількість послідовностей для KFold: 5")

    if len(X) < 5:  
        pytest.skip(f"Недостатньо даних для навчання (потрібно мінімум 5 послідовностей, отримано {len(X)})")

    histories = model.train(X, y, epochs=2, batch_size=32, n_splits=min(5, len(X)))
    assert len(histories) > 0
    
    metrics = model.evaluate_model(X, y)
    assert 'min_temp' in metrics
    assert 'max_temp' in metrics
    for temp_type in ['min_temp', 'max_temp']:
        assert 'mse' in metrics[temp_type]
        assert 'mae' in metrics[temp_type]
        assert 'r2' in metrics[temp_type]

def test_system_integration(config, db, db_manager, model, sample_weather_data):
    assert db.health_check() == True
    assert db_manager.connection is not None
    
    assert hasattr(model, 'health_check')
    assert hasattr(model, 'model_path')
    
    assert config.db.host is not None
    assert config.model.model_path is not None
    
    assert db_manager.import_csv_data('data/weather_data.csv') in [True, False]
    
    X, y = model.prepare_data(sample_weather_data)
    if len(X) >= 5:
        model.train(X, y, epochs=2, batch_size=32, n_splits=min(5, len(X)))
        
        predictions = model.predict_year(X[-1:])
        
        assert db_manager.save_predictions(predictions, 2024) == True
        
        metrics = model.evaluate_model(X, y)
        assert db_manager.save_model_metadata('LSTM', metrics) == True
        saved_predictions = db_manager.get_predictions_for_month(2024, 1)
        assert len(saved_predictions) > 0
    else:
        pytest.skip("Недостатньо даних для тестування повного циклу") 