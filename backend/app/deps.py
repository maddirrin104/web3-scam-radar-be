from fastapi import Depends
from sqlalchemy.orm import Session
from app.db import get_db

def get_db_session(db: Session = Depends(get_db)) -> Session:
    return db