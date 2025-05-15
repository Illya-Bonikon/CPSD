# Паралельний Генетичний Алгоритм для задачі комівояжера

## Опис проекту
Реалізація паралельного генетичного алгоритму для розв'язання задачі комівояжера (TSP) з веб-інтерфейсом для візуалізації процесу еволюції.

## Функціональність
- Паралельна обробка популяцій
- Налаштовувані параметри алгоритму:
  - Розмір популяції
  - Кількість ітерацій
  - Методи вибору батьків
  - Оператори кросоверу та мутації
- Візуалізація процесу еволюції
- Збереження історії еволюції в MongoDB
- Експорт результатів у CSV

## Технічний стек
### Backend
- Python 3.8+
- FastAPI
- MongoDB
- NumPy
- NetworkX
- Pytest (для тестів)

### Frontend
- React
- React Force Graph
- Recharts
- Tailwind CSS

## Встановлення та запуск

### Backend
1. Створіть віртуальне середовище:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```

2. Встановіть залежності:
```bash
pip install -r requirements.txt
```

3. Запустіть MongoDB

4. Запустіть сервер:
```bash
cd backend
uvicorn app.main:app --reload
```

### Frontend
1. Встановіть залежності:
```bash
cd frontend
npm install
```

2. Запустіть розробничий сервер:
```bash
npm start
```

## Тестування
```bash
cd backend
pytest
```

## Структура проекту
```
├── backend/
│   ├── app/
│   │   ├── core/           # Основна логіка ГА
│   │   ├── parallel/       # Паралельні обчислення
│   │   ├── graph/          # Робота з графами
│   │   ├── database/       # Робота з БД
│   │   ├── api/           # REST API
│   │   └── tests/         # Тести
│   └── requirements.txt
│
├── frontend/
│   └── src/
│       ├── components/    # React компоненти
│       ├── pages/        # Сторінки
│       ├── services/     # API сервіси
│       └── utils/        # Утиліти
│
└── README.md
``` 