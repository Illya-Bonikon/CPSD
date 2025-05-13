import mysql.connector
import pandas as pd
from datetime import datetime
import json
from typing import List, Dict, Any

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
        self.create_tables()
        
    def connect(self):
        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="SQL55455445kjk.SQL",
            database="weather_prediction"
        )
        
    def create_tables(self):
        cursor = self.connection.cursor()
        
        # Створюємо таблиці з SQL файлу
        with open('database/lab3.sql', 'r') as file:
            sql_commands = file.read()
            for command in sql_commands.split(';'):
                if command.strip():
                    cursor.execute(command)
        
        self.connection.commit()
        cursor.close()
        
    def import_csv_data(self, csv_path: str) -> bool:
        """Імпорт даних з CSV файлу в базу даних"""
        cursor = None
        try:
            df = pd.read_csv(csv_path)
            cursor = self.connection.cursor()
            
            # Перевіряємо чи є дані в таблиці
            cursor.execute("SELECT COUNT(*) FROM temperature_data")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Заповнюємо NaN значення значеннями з попередньої години
                df['Basel Temperature [2 m elevation corrected]'] = df['Basel Temperature [2 m elevation corrected]'].fillna(method='ffill')
                
                # Якщо все ще залишились NaN значення (наприклад, на початку файлу),
                # заповнюємо їх значеннями з наступної години
                df['Basel Temperature [2 m elevation corrected]'] = df['Basel Temperature [2 m elevation corrected]'].fillna(method='bfill')
                
                # Імпортуємо дані з CSV
                for _, row in df.iterrows():
                    timestamp = datetime.strptime(row['timestamp'], '%Y%m%dT%H%M')
                    temperature = row['Basel Temperature [2 m elevation corrected]']
                    
                    cursor.execute("""
                        INSERT INTO temperature_data (timestamp, temperature)
                        VALUES (%s, %s)
                    """, (timestamp, temperature))
                
                self.connection.commit()
                print(f"Імпортовано {len(df)} записів")
                return True
            return False
            
        except Exception as e:
            print(f"Помилка при імпорті даних: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
        
    def get_all_data(self) -> pd.DataFrame:
        """Отримання всіх даних з бази даних"""
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT timestamp, temperature FROM temperature_data ORDER BY timestamp")
        data = cursor.fetchall()
        cursor.close()
        
        return pd.DataFrame(data)
    
    def save_predictions(self, predictions: List[Dict[str, Any]], year: int) -> bool:
        """Збереження прогнозів в базу даних"""
        try:
            cursor = self.connection.cursor()
            
            # Видаляємо старі прогнози для цього року
            cursor.execute("DELETE FROM predictions WHERE YEAR(date) = %s", (year,))
            
            # Додаємо нові прогнози
            start_date = datetime(year, 1, 1)
            for i, pred in enumerate(predictions):
                current_date = start_date + pd.Timedelta(days=i)
                cursor.execute("""
                    INSERT INTO predictions (date, min_temperature, max_temperature)
                    VALUES (%s, %s, %s)
                """, (current_date.date(), pred['min_temp'], pred['max_temp']))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            print(f"Помилка при збереженні прогнозів: {e}")
            return False
        finally:
            cursor.close()
    
    def save_model_metadata(self, model_type: str, metrics: Dict[str, float]) -> bool:
        """Збереження метаданих моделі"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO models_metadata (model_type, training_date, metrics)
                VALUES (%s, %s, %s)
            """, (model_type, datetime.now().date(), json.dumps(metrics)))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            print(f"Помилка при збереженні метаданих моделі: {e}")
            return False
        finally:
            cursor.close()
        
    def close(self):
        """Закриття з'єднання з базою даних"""
        if self.connection:
            self.connection.close()

    def get_predictions_for_month(self, year: int, month: int) -> pd.DataFrame:
        """Отримання прогнозів для конкретного місяця"""
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT date, min_temperature, max_temperature 
            FROM predictions 
            WHERE YEAR(date) = %s AND MONTH(date) = %s 
            ORDER BY date
        """, (year, month))
        data = cursor.fetchall()
        cursor.close()
        
        return pd.DataFrame(data) 