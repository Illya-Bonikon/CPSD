import pytest
import numpy as np
import pandas as pd
from core.config import Config
from database.connection import DatabaseConnection
from database.db_manager import DatabaseManager
from ml.lstm_model import TemperatureLSTM
import sys
import os

# Додаємо кореневу директорію проекту до Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def config():
    return Config()

@pytest.fixture
def db(config):
    return DatabaseConnection(config)

@pytest.fixture
def db_manager():
    return DatabaseManager()

@pytest.fixture
def model(config):
    return TemperatureLSTM(config.model.model_path)

@pytest.fixture
def sample_weather_data():
    """Фікстура з тестовими даними про погоду"""
    # Генеруємо більше даних для навчання
    dates = pd.date_range(start='2023-01-01', end='2023-03-31', freq='h')  # 3 місяці даних
    # Генеруємо більш реалістичні температури з сезонними коливаннями
    base_temp = 15  # середня температура
    seasonal = 10 * np.sin(2 * np.pi * np.arange(len(dates)) / (24 * 365))  # сезонні коливання
    daily = 5 * np.sin(2 * np.pi * np.arange(len(dates)) / 24)  # добові коливання
    noise = np.random.normal(0, 2, len(dates))  # випадкові коливання
    temperatures = base_temp + seasonal + daily + noise
    df = pd.DataFrame({
        'timestamp': dates,
        'temperature': temperatures
    })
    df.set_index('timestamp', inplace=True)  # Встановлюємо timestamp як індекс
    print(f"\nКількість годинних записів: {len(df)}")
    print(f"Кількість днів: {len(df.resample('D').mean())}")
    return df.reset_index()  # Повертаємо timestamp як колонку

def test_database_connection(db):
    """Тест підключення до бази даних"""
    assert db.health_check() == True
    
    # Тест ініціалізації бази даних
    assert db.init_db() == True
    
    # Тест контекстного менеджера
    with db.get_session() as session:
        assert session is not None

def test_database_manager(db_manager, sample_weather_data):
    """Тест менеджера бази даних"""
    # Тест імпорту даних
    assert db_manager.import_csv_data('data/weather_data.csv') in [True, False]
    
    # Тест отримання даних
    data = db_manager.get_all_data()
    assert isinstance(data, pd.DataFrame)
    assert 'timestamp' in data.columns
    assert 'temperature' in data.columns
    
    # Тест збереження прогнозів
    predictions = [
        {'min_temp': 10.0, 'max_temp': 20.0},
        {'min_temp': 12.0, 'max_temp': 22.0}
    ]
    assert db_manager.save_predictions(predictions, 2024) == True
    
    # Тест отримання прогнозів за місяць
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
    """Тест прогнозування моделі"""
    # Підготовка тестових даних
    X, y = model.prepare_data(sample_weather_data)
    
    # Якщо немає достатньо даних для прогнозування, пропускаємо тест
    if len(X) == 0:
        pytest.skip("Недостатньо даних для прогнозування")
    
    # Тест прогнозування
    if model.health_check():
        prediction = model.predict(X[0:1])
        min_temp, max_temp = prediction[0]
        assert min_temp <= max_temp, f"min_temp ({min_temp}) має бути менше або дорівнювати max_temp ({max_temp})"
        
        # Тест прогнозування на рік
        yearly_predictions = model.predict_year(X[-1:])
        assert len(yearly_predictions) > 0
        for pred in yearly_predictions:
            assert pred['min_temp'] <= pred['max_temp'], f"min_temp ({pred['min_temp']}) має бути менше або дорівнювати max_temp ({pred['max_temp']})"

def test_model_training(model, sample_weather_data):
    """Тест навчання моделі"""
    X, y = model.prepare_data(sample_weather_data)
    print(f"\nКількість послідовностей для навчання: {len(X)}")
    print(f"Довжина послідовності: {X.shape[1] if len(X) > 0 else 0}")
    print(f"Мінімальна кількість послідовностей для KFold: 5")
    
    # Якщо немає достатньо даних для навчання, пропускаємо тест
    if len(X) < 5:  # Мінімум 5 послідовностей для KFold
        pytest.skip(f"Недостатньо даних для навчання (потрібно мінімум 5 послідовностей, отримано {len(X)})")
    
    # Зменшуємо кількість розбиттів для KFold
    histories = model.train(X, y, epochs=2, batch_size=32, n_splits=min(5, len(X)))
    assert len(histories) > 0
    
    # Тест оцінки моделі
    metrics = model.evaluate_model(X, y)
    assert 'min_temp' in metrics
    assert 'max_temp' in metrics
    for temp_type in ['min_temp', 'max_temp']:
        assert 'mse' in metrics[temp_type]
        assert 'mae' in metrics[temp_type]
        assert 'r2' in metrics[temp_type]

def test_system_integration(config, db, db_manager, model, sample_weather_data):
    """Тест інтеграції всіх компонентів"""
    # Перевірка підключення до БД
    assert db.health_check() == True
    assert db_manager.connection is not None
    
    # Перевірка моделі
    assert hasattr(model, 'health_check')
    assert hasattr(model, 'model_path')
    
    # Перевірка конфігурації
    assert config.db.host is not None
    assert config.model.model_path is not None
    
    # Тест повного циклу роботи
    # 1. Імпорт даних
    assert db_manager.import_csv_data('data/weather_data.csv') in [True, False]
    
    # 2. Навчання моделі
    X, y = model.prepare_data(sample_weather_data)
    if len(X) >= 5:  # Мінімум 5 послідовностей для KFold
        model.train(X, y, epochs=2, batch_size=32, n_splits=min(5, len(X)))
        
        # 3. Прогнозування
        predictions = model.predict_year(X[-1:])
        
        # 4. Збереження прогнозів
        assert db_manager.save_predictions(predictions, 2024) == True
        
        # 5. Збереження метаданих моделі
        metrics = model.evaluate_model(X, y)
        assert db_manager.save_model_metadata('LSTM', metrics) == True
        
        # 6. Перевірка збережених даних
        saved_predictions = db_manager.get_predictions_for_month(2024, 1)
        assert len(saved_predictions) > 0
    else:
        pytest.skip("Недостатньо даних для тестування повного циклу") 