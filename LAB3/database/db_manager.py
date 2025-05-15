import json
import mysql.connector
import pandas as pd

from datetime import datetime
from typing import List, Dict, Any
from contextlib import contextmanager

from core.config import DatabaseConfig


class DatabaseManager:
    DEFAULT_COLUMN = "temperature"

    def __init__(self, db_config: DatabaseConfig):
        self.db_config = db_config
        self.connection = None
        self.connect()
        self.create_tables()

    def connect(self):
        self.connection = mysql.connector.connect(
            host=self.db_config.host,
            user=self.db_config.user,
            password=self.db_config.password,
            database=self.db_config.name,
            port=self.db_config.port
        )

    @contextmanager
    def db_cursor(self, dictionary: bool = False):
        cursor = self.connection.cursor(dictionary=dictionary)
        try:
            yield cursor
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def create_tables(self):
        with self.db_cursor() as cursor:
            with open("database/lab3.sql", 'r') as file:
                sql_commands = file.read()
                for command in sql_commands.split(';'):
                    if command.strip():
                        cursor.execute(command)

    def import_csv_data(self, csv_path: str) -> bool:
        try:
            df = pd.read_csv(csv_path)

            with self.db_cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM temperature_data")
                count = cursor.fetchone()[0]

                if count == 0:
                    df = self.fill_missing_temperatures(df, self.DEFAULT_COLUMN)
                    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y%m%dT%H%M", errors="coerce")

                    for _, row in df.iterrows():
                        if pd.isna(row["timestamp"]):
                            continue
                        temperature = row[self.DEFAULT_COLUMN]
                        cursor.execute("""
                            INSERT INTO temperature_data (timestamp, temperature)
                            VALUES (%s, %s)
                        """, (row["timestamp"], temperature))

                    print(f"Імпортовано {len(df)} записів")
                    return True
                return False

        except Exception as e:
            print(f"Помилка при імпорті даних: {e}")
            return False

    @staticmethod
    def fill_missing_temperatures(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
        df[column_name] = df[column_name].fillna(method="ffill").fillna(method="bfill")
        return df

    def get_all_data(self) -> pd.DataFrame:
        with self.db_cursor(dictionary=True) as cursor:
            cursor.execute("SELECT timestamp, temperature FROM temperature_data ORDER BY timestamp")
            data = cursor.fetchall()
        return pd.DataFrame(data)

    def save_predictions(self, predictions: List[Dict[str, Any]], year: int) -> bool:
        try:
            with self.db_cursor() as cursor:
                cursor.execute("DELETE FROM predictions WHERE YEAR(date) = %s", (year,))
                start_date = datetime(year, 1, 1)

                for i, pred in enumerate(predictions):
                    current_date = start_date + pd.Timedelta(days=i)
                    cursor.execute("""
                        INSERT INTO predictions (date, min_temperature, max_temperature)
                        VALUES (%s, %s, %s)
                    """, (current_date.date(), pred["min_temp"], pred["max_temp"]))

            return True

        except Exception as e:
            print(f"Помилка при збереженні прогнозів: {e}")
            return False

    def save_model_metadata(self, model_type: str, metrics: Dict[str, float]) -> bool:
        try:
            with self.db_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO models_metadata (model_type, training_date, metrics)
                    VALUES (%s, %s, %s)
                """, (model_type, datetime.now().date(), json.dumps(metrics)))

            return True

        except Exception as e:
            print(f"Помилка при збереженні метаданих моделі: {e}")
            return False

    def get_predictions_for_month(self, year: int, month: int) -> pd.DataFrame:
        with self.db_cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT date, min_temperature, max_temperature 
                FROM predictions 
                WHERE YEAR(date) = %s AND MONTH(date) = %s 
                ORDER BY date
            """, (year, month))
            data = cursor.fetchall()
        return pd.DataFrame(data)

    def close(self):
        if self.connection:
            self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
