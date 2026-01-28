from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Purchase, Perfume
from app.schemas import PurchaseCreate, PurchaseRead

router = APIRouter(prefix="/purchases", tags=["Purchases"])

@router.post("", response_model=PurchaseRead, status_code=status.HTTP_201_CREATED)
def create_purchase(purchase_in: PurchaseCreate, db: Session = Depends(get_db)):
    perfume = db.query(Perfume).filter(Perfume.id == purchase_in.perfume_id).first()

    if not perfume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfume not found")

    purchase = Purchase(
        perfume_id=purchase_in.perfume_id,
        date=purchase_in.date,
        price=purchase_in.price,
        store=purchase_in.store,
        ml=purchase_in.ml,
    )

    db.add(purchase)
    db.commit()
    db.refresh(purchase)

    return purchase

@router.get("", response_model=List[PurchaseRead])
def list_purchases(db: Session = Depends(get_db)):
    return db.query(Purchase).all()

@router.get("/{purchase_id}", response_model=PurchaseRead)
def get_purchase(purchase_id: int, db: Session = Depends(get_db)):
    purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()

    if not purchase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase not found")

    return purchase