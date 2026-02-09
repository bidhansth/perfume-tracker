from typing import Optional, List
from datetime import date as date_type
from enum import Enum
from sqlalchemy import String, Float, ForeignKey, Date, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class Role(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"

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

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    role: Mapped[Role] = mapped_column(SQLEnum(Role, name="role"), default=Role.USER)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[date_type] = mapped_column(Date, default=date_type.today)

    perfumes: Mapped[List["Perfume"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    purchases: Mapped[List["Purchase"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Perfume(Base):
    __tablename__ = "perfumes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    brand: Mapped[str] = mapped_column(String)
    concentration: Mapped[Concentration] = mapped_column(SQLEnum(Concentration, name="concentration"))
    season: Mapped[Season] = mapped_column(SQLEnum(Season, name="season"))
    available: Mapped[bool] = mapped_column(default=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    owner: Mapped["User"] = relationship(back_populates="perfumes")
    purchases: Mapped[List["Purchase"]] = relationship(back_populates="perfume", cascade="all, delete-orphan")

class Purchase(Base):
    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    perfume_id: Mapped[int] = mapped_column(ForeignKey("perfumes.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date: Mapped[date_type] = mapped_column(Date)
    price: Mapped[float] = mapped_column(Float)
    store: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    ml: Mapped[int] = mapped_column(default=100)

    perfume: Mapped["Perfume"] = relationship(back_populates="purchases")
    user: Mapped["User"] = relationship(back_populates="purchases")
