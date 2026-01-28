from pydantic import BaseModel
from typing import Optional, List
from .models import Concentration, Season

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
