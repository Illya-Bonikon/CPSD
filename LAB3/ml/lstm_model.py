import keras
import numpy as np
import pandas as pd
import joblib
import os

from datetime import datetime
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from core.config import ModelConfig

class TemperatureLSTM:
    
    def __init__(self, config: ModelConfig):
        self.sequence_length = config.sequence_length
        self.model_path = config.model_path
        self.learning_rate = config.learning_rate
        self.scaler_path = self.model_path.parent / "temperature_scaler.pkl"

        if self.model_path.exists():
            print(f"Завантаження моделі з {self.model_path}")
            self.model = keras.models.load_model(self.model_path)
        else:
            print(f"Модель не знайдено, створюється нова")
            self.model = None 
            
        if self.scaler_path.exists():
            print(f"Завантаження scaler з {self.scaler_path}")
            self.scaler = joblib.load(self.scaler_path)
        else:
            print(f"Scaler не знайдено")
            self.scaler = None
    
    def health_check(self) -> bool:

        try:
            if self.model is None:
                return False

            test_input = np.zeros((1, self.sequence_length, 4))
            self.model.predict(test_input, verbose=0)
            return True
        except Exception as e:
            print(f"Помилка перевірки моделі: {e}")
            return False

    def create_model(self, input_shape):
        model = keras.Sequential([
            keras.layers.Bidirectional(keras.layers.LSTM(128, input_shape=input_shape, return_sequences=True)),
            keras.layers.BatchNormalization(),
            keras.layers.Dropout(0.3),
            keras.layers.Bidirectional(keras.layers.LSTM(64)),
            keras.layers.BatchNormalization(),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(2)
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate),
            loss=keras.losses.Huber(),
            metrics=['mae']
        )
        
        self.model = model
        return model
    
    def prepare_data(self, df):

        if isinstance(df.index, pd.DatetimeIndex):
            df = df.reset_index()
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        daily_data = df.resample('D').agg({
            'temperature': ['min', 'max']
        })
        
        print(f"Кількість днів після групування: {len(daily_data)}")
        
        daily_data['month'] = daily_data.index.month
        daily_data['month_sin'] = np.sin(2 * np.pi * daily_data['month'] / 12)
        daily_data['month_cos'] = np.cos(2 * np.pi * daily_data['month'] / 12)
        
        if self.scaler is None:
            self.scaler = {
                'min': {'mean': daily_data[('temperature', 'min')].mean(),
                       'std': daily_data[('temperature', 'min')].std()},
                'max': {'mean': daily_data[('temperature', 'max')].mean(),
                       'std': daily_data[('temperature', 'max')].std()}
            }
        
        normalized_data = pd.DataFrame({
            'min_temp': (daily_data[('temperature', 'min')] - 
                        self.scaler['min']['mean']) / self.scaler['min']['std'],
            'max_temp': (daily_data[('temperature', 'max')] - 
                        self.scaler['max']['mean']) / self.scaler['max']['std'],
            'month_sin': daily_data['month_sin'],
            'month_cos': daily_data['month_cos']
        })
        
        if len(normalized_data) < self.sequence_length:
            self.sequence_length = len(normalized_data) - 1
        
        X, y = [], []
        for i in range(len(normalized_data) - self.sequence_length):
            X.append(normalized_data.iloc[i:(i + self.sequence_length)].values)
            y.append(normalized_data.iloc[i + self.sequence_length][['min_temp', 'max_temp']].values)
        
        print(f"Кількість послідовностей для навчання: {len(X)}")
        print(f"Довжина послідовності: {self.sequence_length}")
        print(f"Форма X: {np.array(X).shape if len(X) > 0 else (0,)}")
        print(f"Форма y: {np.array(y).shape if len(y) > 0 else (0,)}")
            
        return np.array(X), np.array(y)
    
    def train(self, X, y, epochs=100, batch_size=32, n_splits=5):
        if self.model is None:
            self.create_model((self.sequence_length, 4)) 
        
        kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
        histories = []
        
        for train_idx, val_idx in kf.split(X):
            history = self.model.fit(
                X[train_idx], y[train_idx],
                validation_data=(X[val_idx], y[val_idx]),
                epochs=epochs,
                batch_size=batch_size,
                verbose=1
            )
            histories.append(history.history)
        
        self.model.save(self.model_path)
        joblib.dump(self.scaler, "models/temperature_scaler.pkl")
        
        return histories
    
    def evaluate_model(self, X, y):
        predictions = self.model.predict(X)
        
        denormalized_predictions = []
        denormalized_actual = []
        
        for pred, actual in zip(predictions, y):
            denormalized_pred = {
                'min_temp': pred[0] * self.scaler['min']['std'] + self.scaler['min']['mean'],
                'max_temp': pred[1] * self.scaler['max']['std'] + self.scaler['max']['mean']
            }
            denormalized_actual.append({
                'min_temp': actual[0] * self.scaler['min']['std'] + self.scaler['min']['mean'],
                'max_temp': actual[1] * self.scaler['max']['std'] + self.scaler['max']['mean']
            })
            denormalized_predictions.append(denormalized_pred)
        
        min_temp_pred = np.array([p['min_temp'] for p in denormalized_predictions])
        max_temp_pred = np.array([p['max_temp'] for p in denormalized_predictions])
        min_temp_actual = np.array([a['min_temp'] for a in denormalized_actual])
        max_temp_actual = np.array([a['max_temp'] for a in denormalized_actual])
        
        metrics = {
            'min_temp': {
                'mse': mean_squared_error(min_temp_actual, min_temp_pred),
                'mae': mean_absolute_error(min_temp_actual, min_temp_pred),
                'r2': r2_score(min_temp_actual, min_temp_pred)
            },
            'max_temp': {
                'mse': mean_squared_error(max_temp_actual, max_temp_pred),
                'mae': mean_absolute_error(max_temp_actual, max_temp_pred),
                'r2': r2_score(max_temp_actual, max_temp_pred)
            }
        }
        
        return metrics
    
    def predict(self, X):
        if not self.health_check():
            raise ValueError("Модель не готова до прогнозування")
        predictions = self.model.predict(X, verbose=0)

        return np.sort(predictions, axis=1)

    def predict_year(self, last_sequence):
        predictions = []
        current_sequence = last_sequence.copy()
        
        start_date = datetime.now().replace(month=1, day=1)
        for i in range(365):  # Прогноз на рік
            current_date = start_date + pd.Timedelta(days=i)
            month = current_date.month
            
            month_sin = np.sin(2 * np.pi * month / 12)
            month_cos = np.cos(2 * np.pi * month / 12)
            
            current_sequence[0, :, -2:] = np.array([month_sin, month_cos])
            
            pred = self.model.predict(current_sequence.reshape(1, self.sequence_length, 4), verbose=0)
            pred = np.sort(pred, axis=1)

            denormalized_pred = {
                'min_temp': pred[0][0] * self.scaler['min']['std'] + self.scaler['min']['mean'],
                'max_temp': pred[0][1] * self.scaler['max']['std'] + self.scaler['max']['mean']
            }
            
            current_sequence = np.roll(current_sequence, -1, axis=1) 
            current_sequence[0, -1, :2] = pred[0]  
            
            predictions.append(pred[0])
        
        denormalized_predictions = []
        for pred in predictions:
            denormalized_pred = {
                'min_temp': pred[0] * self.scaler['min']['std'] + self.scaler['min']['mean'],
                'max_temp': pred[1] * self.scaler['max']['std'] + self.scaler['max']['mean']
            }
            denormalized_predictions.append(denormalized_pred)
            
        return denormalized_predictions 