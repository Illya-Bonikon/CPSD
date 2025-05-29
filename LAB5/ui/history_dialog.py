from PySide6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView

class HistoryDialog(QDialog):
    def __init__(self, db_logger, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Історія запусків")
        self.resize(800, 400)
        self.db_logger = db_logger
        self.selected_run = None
        self._init_ui()
        self.load_runs()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Дата", "Вершин", "Мін. вага", "Макс. вага", "Епох", "Островів"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.cellDoubleClicked.connect(self.select_run)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_runs(self):
        runs = list(self.db_logger.runs.find().sort("datetime", -1))
        self.runs = runs
        self.table.setRowCount(len(runs))
        for i, run in enumerate(runs):
            dt = run.get("datetime", "")
            params = run.get("params", {})
            self.table.setItem(i, 0, QTableWidgetItem(str(dt)[:19]))
            self.table.setItem(i, 1, QTableWidgetItem(str(params.get("n", ""))))
            self.table.setItem(i, 2, QTableWidgetItem(str(params.get("w_min", ""))))
            self.table.setItem(i, 3, QTableWidgetItem(str(params.get("w_max", ""))))
            self.table.setItem(i, 4, QTableWidgetItem(str(params.get("epochs", ""))))
            self.table.setItem(i, 5, QTableWidgetItem(str(params.get("n_islands", ""))))

    def select_run(self, row, col):
        self.selected_run = self.runs[row]
        self.accept() 