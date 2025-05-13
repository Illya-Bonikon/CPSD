# conftest.py
import sys
import os

# Додаємо кореневу директорію проекту до Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)