import numpy as np
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpinBox, QTableWidget, QTableWidgetItem, QGroupBox, QFormLayout, QLineEdit)
from PySide6.QtCore import QTimer
from core.graph import GraphGenerator
from core.ga import ParallelGA
from core.db import MongoLogger
from ui.graph_canvas import GraphCanvas
from ui.history_dialog import HistoryDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TSP: Паралельний генетичний алгоритм")
        self.resize(1200, 800)
        self.db_logger = MongoLogger()
        self._init_ui()
        self.stats = []
        self.graph = None
        self.current_gen = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_generation)
        self.is_playing = False

    def _init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        
        top_layout = QHBoxLayout()
        
        left_btns = QVBoxLayout()
        self.run_btn = QPushButton("Запустити")
        self.run_btn.clicked.connect(self.run_algorithm)
        self.history_btn = QPushButton("Історія запусків")
        self.history_btn.clicked.connect(self.show_history)
        self.prev_btn = QPushButton("⏮ Попередня")
        self.prev_btn.clicked.connect(self.prev_generation)
        self.play_btn = QPushButton("▶ Авто")
        self.play_btn.clicked.connect(self.toggle_play)
        self.next_btn = QPushButton("Наступна ⏭")
        self.next_btn.clicked.connect(self.next_generation)
        self.gen_label = QLabel("Генерація: -/-")
        left_btns.addWidget(self.run_btn)
        left_btns.addWidget(self.history_btn)
        left_btns.addSpacing(20)
        left_btns.addWidget(self.prev_btn)
        left_btns.addWidget(self.play_btn)
        left_btns.addWidget(self.next_btn)
        left_btns.addWidget(self.gen_label)
        left_btns.addStretch()

        
        params_group = QGroupBox("Параметри задачі")
        params_layout = QFormLayout()
        self.vertex_spin = QSpinBox()
        self.vertex_spin.setRange(4, 100)
        self.vertex_spin.setValue(10)
        self.weight_min = QSpinBox()
        self.weight_min.setRange(1, 1000)
        self.weight_min.setValue(1)
        self.weight_max = QSpinBox()
        self.weight_max.setRange(1, 1000)
        self.weight_max.setValue(100)
        self.epochs_spin = QSpinBox()
        self.epochs_spin.setRange(1, 10000)
        self.epochs_spin.setValue(100)
        self.pop_spin = QSpinBox()
        self.pop_spin.setRange(2, 1000)
        self.pop_spin.setValue(100)
        self.mut_spin = QLineEdit("0.05")
        self.cross_spin = QLineEdit("0.7")
        self.islands_spin = QSpinBox()
        self.islands_spin.setRange(1, 16)
        self.islands_spin.setValue(4)
        params_layout.addRow("Кількість вершин:", self.vertex_spin)
        params_layout.addRow("Мін. вага:", self.weight_min)
        params_layout.addRow("Макс. вага:", self.weight_max)
        params_layout.addRow("Кількість епох:", self.epochs_spin)
        params_layout.addRow("Розмір популяції:", self.pop_spin)
        params_layout.addRow("Ймовірність мутації:", self.mut_spin)
        params_layout.addRow("Ймовірність кросоверу:", self.cross_spin)
        params_layout.addRow("Кількість островів:", self.islands_spin)
        params_group.setLayout(params_layout)

        top_layout.addLayout(left_btns, 1)
        top_layout.addWidget(params_group, 3)

        
        self.canvas = GraphCanvas()
        self.canvas.setMinimumHeight(500)
        self.stats_table = QTableWidget(1, 3)
        self.stats_table.setHorizontalHeaderLabels(["Найкращий", "Найгірший", "Середній"])
        self.stats_table.setVerticalHeaderLabels(["Довжина шляху"])
        legend = QLabel("<span style='color:blue;'>Синій</span> — найкращий, <span style='color:green;'>Зелений</span> — 2-й найкращий, <span style='color:red;'>Червоний</span> — найгірший шлях")

        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.canvas)
        main_layout.addWidget(legend)
        main_layout.addWidget(self.stats_table)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def run_algorithm(self):
        n = self.vertex_spin.value()
        w_min = self.weight_min.value()
        w_max = self.weight_max.value()
        epochs = self.epochs_spin.value()
        pop_size = self.pop_spin.value()
        mut_prob = float(self.mut_spin.text())
        cross_prob = float(self.cross_spin.text())
        n_islands = self.islands_spin.value()
        generator = GraphGenerator(n, w_min, w_max)
        self.graph = generator.generate()
        ga = ParallelGA(self.graph, pop_size, epochs, mut_prob, cross_prob, n_islands)
        self.stats = ga.run()
        params = {
            'n': n,
            'w_min': w_min,
            'w_max': w_max,
            'epochs': epochs,
            'pop_size': pop_size,
            'mut_prob': mut_prob,
            'cross_prob': cross_prob,
            'n_islands': n_islands
        }
        self.db_logger.save_run(self.graph, params, self.stats)
        self.current_gen = 0
        self.show_generation(self.current_gen)

    def show_generation(self, gen_idx):
        if not self.stats:
            return
        gen_idx = max(0, min(gen_idx, len(self.stats)-1))
        self.current_gen = gen_idx
        stat = self.stats[gen_idx]
        best = stat['best']['path']
        second = stat['second']['path']
        worst = stat['worst']['path']
        self.canvas.set_graph_and_paths(self.graph, best, second, worst)
        self.stats_table.setRowCount(1)
        self.stats_table.setItem(0, 0, QTableWidgetItem(str(stat['best']['length'])))
        self.stats_table.setItem(0, 1, QTableWidgetItem(str(stat['worst']['length'])))
        self.stats_table.setItem(0, 2, QTableWidgetItem(f"{stat['avg']:.2f}"))
        self.gen_label.setText(f"Генерація: {gen_idx+1}/{len(self.stats)}")

    def prev_generation(self):
        if self.stats and self.current_gen > 0:
            self.show_generation(self.current_gen - 1)

    def next_generation(self):
        if self.stats and self.current_gen < len(self.stats)-1:
            self.show_generation(self.current_gen + 1)
        elif self.is_playing:
            self.timer.stop()
            self.is_playing = False
            self.play_btn.setText("▶ Авто")

    def toggle_play(self):
        if not self.stats:
            return
        if not self.is_playing:
            self.is_playing = True
            self.play_btn.setText("⏸ Пауза")
            self.timer.start(400)
        else:
            self.is_playing = False
            self.play_btn.setText("▶ Авто")
            self.timer.stop()

    def show_history(self):
        dlg = HistoryDialog(self.db_logger, self)
        if dlg.exec() == 1 and dlg.selected_run:
            run = dlg.selected_run
            self.graph = np.array(run['graph'])
            self.stats = run['generations']
            self.current_gen = 0
            self.show_generation(self.current_gen) 