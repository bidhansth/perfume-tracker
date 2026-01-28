from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.models import Purchase, Perfume
from app.schemas import PurchaseCreate, PurchaseRead, PaginatedResponse

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

@router.get("", response_model=PaginatedResponse[PurchaseRead])
def list_purchases(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
    ):

    purchases = db.query(Purchase)

    if start_date:
        purchases = purchases.filter(Purchase.date >= start_date)
    if end_date:
        purchases = purchases.filter(Purchase.date <= end_date)
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start date cannot be after end date")
    
    if min_price is not None:
        purchases = purchases.filter(Purchase.price >= min_price)
    if max_price is not None:
        purchases = purchases.filter(Purchase.price <= max_price)
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Minimum price cannot be greater than maximum price")
    
    total = purchases.count()
    items = purchases.offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items
    }

@router.get("/{purchase_id}", response_model=PurchaseRead)
def get_purchase(purchase_id: int, db: Session = Depends(get_db)):
    purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()

    if not purchase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase not found")

    return purchase

@router.delete("/{purchase_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_purchase(purchase_id: int, db: Session = Depends(get_db)):
    purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()

    if not purchase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase not found")

    db.delete(purchase)
    db.commit()

    return purchase
