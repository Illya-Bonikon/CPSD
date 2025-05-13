from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
                             QLabel, QFileDialog, QMessageBox, QProgressBar)
from PySide6.QtCore import Qt, QThread, Signal
import pandas as pd
from datetime import datetime
import sys
import os
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import DatabaseManager
from ml.lstm_model import TemperatureLSTM

class TrainingThread(QThread):
    finished = Signal(dict)
    error = Signal(str)
    
    def __init__(self, model, X, y):
        super().__init__()
        self.model = model
        self.X = X
        self.y = y
        
    def run(self):
        try:
            histories = self.model.train(self.X, self.y)
            # Беремо середні значення метрик з усіх фолдів
            avg_history = {
                'loss': np.mean([h['loss'] for h in histories], axis=0),
                'val_loss': np.mean([h['val_loss'] for h in histories], axis=0),
                'mae': np.mean([h['mae'] for h in histories], axis=0),
                'val_mae': np.mean([h['val_mae'] for h in histories], axis=0)
            }
            self.finished.emit(avg_history)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Прогнозування температури")
        self.setMinimumSize(1000, 800)
        
        self.db_manager = DatabaseManager()
        self.lstm_model = TemperatureLSTM()
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Верхня панель з кнопками
        top_panel = QHBoxLayout()
        
        self.import_btn = QPushButton("Імпортувати CSV")
        self.import_btn.clicked.connect(self.import_csv)
        top_panel.addWidget(self.import_btn)
        
        self.train_btn = QPushButton("Навчити модель")
        self.train_btn.clicked.connect(self.train_model)
        self.train_btn.setEnabled(False)
        top_panel.addWidget(self.train_btn)
        
        self.year_combo = QComboBox()
        self.year_combo.addItems([str(year) for year in range(2025, 2031)])
        top_panel.addWidget(QLabel("Рік прогнозу:"))
        top_panel.addWidget(self.year_combo)
        
        self.predict_btn = QPushButton("Прогнозувати")
        self.predict_btn.clicked.connect(self.make_prediction)
        self.predict_btn.setEnabled(False)
        top_panel.addWidget(self.predict_btn)
        
        layout.addLayout(top_panel)
        
        # Прогрес-бар для навчання
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Таблиця для відображення прогнозу
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Дата", "Мін. температура", "Макс. температура"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
    def import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Виберіть CSV файл", "", "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                if self.db_manager.import_csv_data(file_path):
                    QMessageBox.information(self, "Успіх", "Дані успішно імпортовано")
                    self.train_btn.setEnabled(True)
                else:
                    QMessageBox.information(self, "Інформація", "Дані вже імпортовано")
                    self.train_btn.setEnabled(True)
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Помилка при імпорті: {str(e)}")
                
    def train_model(self):
        try:
            df = self.db_manager.get_all_data()
            X, y = self.lstm_model.prepare_data(df)
            
            self.train_btn.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Невизначений прогрес
            
            self.training_thread = TrainingThread(self.lstm_model, X, y)
            self.training_thread.finished.connect(self.on_training_finished)
            self.training_thread.error.connect(self.on_training_error)
            self.training_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка при підготовці даних: {str(e)}")
            
    def on_training_finished(self, history):
        self.progress_bar.setVisible(False)
        self.train_btn.setEnabled(True)
        self.predict_btn.setEnabled(True)
        
        # Зберігаємо метадані моделі
        self.db_manager.save_model_metadata("LSTM", {
            'final_loss': history['loss'][-1],
            'final_val_loss': history['val_loss'][-1],
            'final_mae': history['mae'][-1],
            'final_val_mae': history['val_mae'][-1]
        })
        
        QMessageBox.information(self, "Успіх", "Модель успішно навчено")
            
    def on_training_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.train_btn.setEnabled(True)
        QMessageBox.critical(self, "Помилка", f"Помилка при навчанні: {error_msg}")
            
    def make_prediction(self):
        try:
            df = self.db_manager.get_all_data()
            X, _ = self.lstm_model.prepare_data(df)
            predictions = self.lstm_model.predict_year(X[-1])
            
            # Зберігаємо прогнози в базу даних
            year = int(self.year_combo.currentText())
            if self.db_manager.save_predictions(predictions, year):
                # Очищаємо таблицю
                self.table.setRowCount(0)
                
                # Додаємо прогнози в таблицю
                start_date = datetime(year, 1, 1)
                for i, pred in enumerate(predictions):
                    current_date = start_date + pd.Timedelta(days=i)
                    
                    row_position = self.table.rowCount()
                    self.table.insertRow(row_position)
                    
                    self.table.setItem(row_position, 0, QTableWidgetItem(current_date.strftime("%Y-%m-%d")))
                    self.table.setItem(row_position, 1, QTableWidgetItem(f"{pred['min_temp']:.1f}°C"))
                    self.table.setItem(row_position, 2, QTableWidgetItem(f"{pred['max_temp']:.1f}°C"))
                
                QMessageBox.information(self, "Успіх", "Прогноз успішно збережено")
            else:
                QMessageBox.critical(self, "Помилка", "Не вдалося зберегти прогноз")
                
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка при прогнозуванні: {str(e)}")
            
    def closeEvent(self, event):
        self.db_manager.close()
        event.accept() 