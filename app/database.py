from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator

DATABASE_URL = "sqlite:///perfumes.db"

engine = create_engine(DATABASE_URL, echo=True, future=True)

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
