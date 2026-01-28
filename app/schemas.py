from pydantic import BaseModel
from typing import Optional, List, Generic, TypeVar
from .models import Concentration, Season
from datetime import date

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

    class Config:
        orm_mode = True

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    limit: int
    offset: int
    items: List[T]
    