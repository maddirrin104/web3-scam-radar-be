from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings


engine = create_engine(settings.database_url, pool_pre_ping=True)


class Base(DeclarativeBase):
pass


SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
db = SessionLocal()
try:
yield db
finally:
db.close()