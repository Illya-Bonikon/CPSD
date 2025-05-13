from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from .models import Base
import logging

logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Базовий клас для помилок бази даних"""
    pass

class ConnectionError(DatabaseError):
    """Помилка підключення до бази даних"""
    pass

class QueryError(DatabaseError):
    """Помилка виконання запиту"""
    pass

class DatabaseConnection:
    def __init__(self, config):
        try:
            self.connection_string = config.db.get_connection_string()
            self.engine = create_engine(
                self.connection_string,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800
            )
            self.Session = sessionmaker(
                bind=self.engine,
                expire_on_commit=False
            )
            logger.info("Ініціалізовано підключення до бази даних")
        except Exception as e:
            logger.error(f"Помилка ініціалізації бази даних: {e}")
            raise ConnectionError(f"Не вдалося ініціалізувати підключення до бази даних: {e}")
        
    def init_db(self) -> bool:
        """Ініціалізація бази даних"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("База даних успішно ініціалізована")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Помилка ініціалізації бази даних: {e}")
            return False
            
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Отримання сесії бази даних як контекстного менеджера"""
        session: Optional[Session] = None
        try:
            session = self.Session()
            yield session
            session.commit()
        except Exception as e:
            if session:
                session.rollback()
            logger.error(f"Помилка в сесії бази даних: {e}")
            raise QueryError(f"Помилка виконання запиту: {e}")
        finally:
            if session:
                session.close()
        
    def health_check(self) -> bool:
        """Перевірка з'єднання з базою даних"""
        try:
            with self.engine.connect() as conn:
                with conn.begin():
                    conn.execute(text("SELECT 1"))
            logger.debug("Перевірка з'єднання з базою даних успішна")
            return True
        except Exception as e:
            logger.error(f"Помилка перевірки з'єднання з базою даних: {e}")
            return False
            
    def close(self):
        """Закриття з'єднання з базою даних"""
        try:
            self.engine.dispose()
            logger.info("З'єднання з базою даних закрито")
        except Exception as e:
            logger.error(f"Помилка закриття з'єднання з базою даних: {e}")
            raise ConnectionError(f"Не вдалося закрити з'єднання з базою даних: {e}")
            
    def __enter__(self):
        """Контекстний менеджер для підключення до бази даних"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Закриття з'єднання при виході з контексту"""
        self.close() 
        
	