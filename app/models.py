from typing import Optional, List
from datetime import date as date_type, datetime, timezone
from enum import Enum
from sqlalchemy import Boolean, String, Float, ForeignKey, Date, DateTime, Enum as SQLEnum, UniqueConstraint
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
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)
    hashed_password: Mapped[str | None] = mapped_column(String, nullable=True)
    role: Mapped[Role] = mapped_column(SQLEnum(Role, name="role"), default=Role.USER)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    perfumes: Mapped[List["Perfume"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    purchases: Mapped[List["Purchase"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    oauth_identities: Mapped[List["OAuthIdentity"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    @property
    def is_oauth_user(self) -> bool:
        return self.hashed_password is None

class OAuthIdentity(Base):
    __tablename__ = "oauth_identities"
    __table_args__ = (
        UniqueConstraint("provider", "provider_sub", name="uq_provider_sub"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    provider: Mapped[str] = mapped_column(String(50), index=True)  # "google", "github", etc.
    provider_sub: Mapped[str] = mapped_column(String(255))  # Provider's user ID
    provider_email: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship(back_populates="oauth_identities")

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
