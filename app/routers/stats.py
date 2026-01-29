from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.auth import get_current_active_user
from app.database import get_db
from app.models import Purchase, Perfume, User

router = APIRouter(prefix="/stats", tags=["Stats"])

@router.get("/spending")
def spending_stats(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
    ):

    spending_stats = db.query(
        func.sum(Purchase.price).label("total_spent"),
        func.count(Purchase.id).label("total_purchases"),
        func.avg(Purchase.price).label("average_price")
    )
    spending_stats = spending_stats.filter(Purchase.user_id == current_user.id)

    if start_date:
        spending_stats = spending_stats.filter(Purchase.date >= start_date)
    if end_date:
        spending_stats = spending_stats.filter(Purchase.date <= end_date)
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date cannot be after end date")

    result = spending_stats.one()

    return {
        "total_spent": result.total_spent or 0,
        "total_purchases": result.total_purchases or 0,
        "average_price": round(result.average_price,2) if result.average_price else 0
    }

@router.get("/most_expensive")
def most_expensive(
    num : Optional[int] = Query(5, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
    ):

    most_expensive = db.query(Perfume.name, Perfume.brand, Purchase.price, Purchase.date).\
        join(Purchase, Perfume.id == Purchase.perfume_id).\
        filter(Purchase.user_id == current_user.id).\
        order_by(desc(Purchase.price)).\
        limit(num).all()
    
    return [
        {
            "rank": rank,
            "perfume_name": item.name,
            "brand": item.brand,
            "price": item.price,
            "date": item.date
        }
        for rank, item in enumerate(most_expensive, start=1)
    ]