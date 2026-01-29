from typing import Optional
from datetime import date
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from .database import Base

class Concentration(str, Enum):
    EDC = "EDC"
    EDT = "EDT"
    EDP = "EDP"
    PARFUM = "PARFUM"
    OTHER = "OTHER"

class Season(str, Enum):
    SUMMER = "SUMMER"
    WINTER = "WINTER"
    ALL = "ALL"
    OTHER = "OTHER"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(Date, default=date.today, nullable=False)

    perfumes = relationship("Perfume", back_populates="owner", cascade="all, delete-orphan")
    purchases = relationship("Purchase", back_populates="user", cascade="all, delete-orphan")

class Perfume(Base):
    __tablename__ = "perfumes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    brand = Column(String, nullable= False)
    concentration = Column(SQLEnum(Concentration, name="concentration"), nullable= False)
    season = Column(SQLEnum(Season, name="season"), nullable= False)
    available = Column(Boolean, nullable= False, default= True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="perfumes")
    purchases = relationship("Purchase", back_populates= "perfume", cascade="all, delete-orphan")

class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    perfume_id = Column(Integer, ForeignKey("perfumes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    price = Column(Float, nullable=False)
    store = Column(String, nullable=True)
    ml = Column(Integer, default=100)

    perfume = relationship("Perfume", back_populates="purchases")
    user = relationship("User", back_populates="purchases")