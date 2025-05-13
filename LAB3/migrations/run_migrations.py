import os
import sys
import mysql.connector
from dotenv import load_dotenv

def run_migrations():
    """Запуск міграцій бази даних"""
    load_dotenv()
    
    # Параметри підключення до бази даних
    db_params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', 3306),
        'database': os.getenv('DB_NAME', 'weather_prediction'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', '')
    }
    
    try:
        # Підключення до бази даних
        conn = mysql.connector.connect(**db_params)
        cur = conn.cursor()
        
        # Читання та виконання міграцій
        migrations_dir = os.path.dirname(os.path.abspath(__file__))
        migration_files = sorted([f for f in os.listdir(migrations_dir) if f.endswith('.sql')])
        
        for migration_file in migration_files:
            print(f"Застосування міграції: {migration_file}")
            
            with open(os.path.join(migrations_dir, migration_file), 'r') as f:
                sql = f.read()
                # Виконуємо кожен SQL-запит окремо
                for statement in sql.split(';'):
                    if statement.strip():
                        cur.execute(statement)
                
        conn.commit()
        print("Міграції успішно застосовано")
        
    except Exception as e:
        print(f"Помилка при застосуванні міграцій: {e}")
        sys.exit(1)
        
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    run_migrations() 