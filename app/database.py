from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator
from app.config import settings

engine = create_engine(
    str(settings.DATABASE_URL),
    echo=settings.DB_ECHO,
    pool_size=3,
    max_overflow=10,
    future=True)

SessionLocal = sessionmaker(
    bind= engine,
    autoflush= False,
    autocommit= False,
    future= True 
)

Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
