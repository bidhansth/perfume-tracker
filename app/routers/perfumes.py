from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import asc, desc

from app.database import get_db
from app.models import Perfume, Purchase
from app.schemas import PerfumeCreate, PerfumeRead, PurchaseRead

router = APIRouter(prefix="/perfumes", tags=["Perfumes"])

@router.post("", response_model=PerfumeRead, status_code=status.HTTP_201_CREATED)
def create_perfume(perfume_in: PerfumeCreate, db: Session = Depends(get_db)):
    perfume = Perfume(
        name = perfume_in.name,
        brand = perfume_in.brand,
        concentration = perfume_in.concentration,
        season = perfume_in.season,
        available = perfume_in.available
    )

    db.add(perfume)
    db.commit()
    db.refresh(perfume)
    return perfume

@router.get("", response_model=List[PerfumeRead])
def list_perfumes(
    available: Optional[bool] = Query(None),
    concentration: Optional[str] = Query(None),
    season: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None, description="Sort by: name, brand"),
    order: str = Query("asc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db)
    ):

    perfumes = db.query(Perfume)
    
    if available is not None:
        perfumes = perfumes.filter(Perfume.available == available)
    if concentration is not None:
        perfumes = perfumes.filter(Perfume.concentration == concentration)
    if season is not None:
        perfumes = perfumes.filter(Perfume.season == season)
    if brand is not None:
        perfumes = perfumes.filter(Perfume.brand.ilike(f"%{brand}%"))

    allowed_sort_fields = {"name": Perfume.name, "brand": Perfume.brand}

    if sort_by:
        if sort_by not in allowed_sort_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort_by field. Allowed fields are: {', '.join(allowed_sort_fields.keys())}"
            )
        
        column = allowed_sort_fields[sort_by]
        perfumes = perfumes.order_by(asc(column) if order == "asc" else desc(column))

    return perfumes.all()

@router.get("/{perfume_id}", response_model=PerfumeRead)
def get_perfume(perfume_id: int, db: Session = Depends(get_db)):
    perfume = db.query(Perfume).filter(Perfume.id == perfume_id).first()

    if not perfume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfume not found"
        )

    return perfume

@router.get("/{perfume_id}/purchases", response_model=List[PurchaseRead])
def get_perfume_purchases(perfume_id: int, db: Session = Depends(get_db)):
    perfume = db.query(Perfume).filter(Perfume.id == perfume_id).first()

    if not perfume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfume not found"
        )

    return perfume.purchases