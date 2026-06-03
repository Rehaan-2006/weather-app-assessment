from sqlalchemy.orm import Session
from app import models, schemas

def get_weather_log(db: Session, log_id: int):
    return db.query(models.WeatherLog).filter(models.WeatherLog.id == log_id).first()

def get_all_weather_logs(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.WeatherLog).offset(skip).limit(limit).all()

def create_weather_log(db: Session, log_data: dict):
    db_log = models.WeatherLog(**log_data)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def delete_weather_log(db: Session, log_id: int):
    db_log = db.query(models.WeatherLog).filter(models.WeatherLog.id == log_id).first()
    if db_log:
        db.delete(db_log)
        db.commit()
        return True
    return False


def update_weather_log(db: Session, log_id: int, updated_fields: dict):
    db_log = db.query(models.WeatherLog).filter(models.WeatherLog.id == log_id).first()
    if not db_log:
        return None
    
    for key, value in updated_fields.items():
        setattr(db_log, key, value)
        
    db.commit()
    db.refresh(db_log)
    return db_log