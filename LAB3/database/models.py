from sqlalchemy import Column, Integer, Float, String, Date, DateTime, Index, ForeignKey, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class WeatherData(Base):
    __tablename__ = 'weather_data'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, index=True)
    hour = Column(Integer, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=True)
    pressure = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_weather_date_hour', 'date', 'hour', unique=True),
    )

class Prediction(Base):
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, index=True)
    hour = Column(Integer, nullable=False)
    predicted_temperature = Column(Float, nullable=False)
    confidence = Column(Float, nullable=True)
    model_id = Column(Integer, ForeignKey('models_metadata.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    model = relationship("ModelMetadata", back_populates="predictions")

    __table_args__ = (
        Index('idx_prediction_date_hour', 'date', 'hour'),
    )

class ModelMetadata(Base):
    __tablename__ = 'models_metadata'
    
    id = Column(Integer, primary_key=True)
    model_path = Column(String, nullable=False)
    model_type = Column(String, nullable=False)
    version = Column(String, nullable=False)
    metrics = Column(JSON, nullable=False)
    hyperparameters = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    predictions = relationship("Prediction", back_populates="model")

    __table_args__ = (
        Index('idx_model_created_at', 'created_at'),
    ) 