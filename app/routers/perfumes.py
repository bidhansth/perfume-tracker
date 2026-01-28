from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

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
def list_perfumes(db: Session = Depends(get_db)):
    perfumes = db.query(Perfume).all()
    return perfumes

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