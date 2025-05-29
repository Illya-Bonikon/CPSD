import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = MainWindow()

    def run(self):
        self.window.showMaximized()
        sys.exit(self.app.exec()) 