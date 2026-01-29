from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Generic, TypeVar
from .models import Concentration, Season
from datetime import date

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50,)
    email: EmailStr = Field(..., description="Email address")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password min 6 characters")

class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: date

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class PerfumeBase(BaseModel):
    name: str
    brand: str
    concentration: Concentration
    season : Season
    available: bool = True

class PerfumeCreate(PerfumeBase):
    pass

class PerfumeRead(PerfumeBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

class PerfumeList(BaseModel):
    items: List[PerfumeRead]
    total: int

# purchase schemas

class PurchaseBase(BaseModel):
    perfume_id: int
    date: date
    price: float
    store: str
    ml: int = 100

class PurchaseCreate(PurchaseBase):
    pass

class PurchaseRead(PurchaseBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    limit: int
    offset: int
    items: List[T]
