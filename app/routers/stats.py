from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, desc, select

from app.auth import get_current_active_user
from app.database import get_db
from app.models import Purchase, Perfume, User

router = APIRouter(prefix="/stats", tags=["Stats"])

@router.get("/spending")
async def spending_stats(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
    ):

    stmt = select(
        func.sum(Purchase.price).label("total_spent"),
        func.count(Purchase.id).label("total_purchases"),
        func.avg(Purchase.price).label("average_price")
        ).where(Purchase.user_id == current_user.id)

    if start_date:
        stmt = stmt.where(Purchase.date >= start_date)
    if end_date:
        stmt = stmt.where(Purchase.date <= end_date)
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date cannot be after end date")

    result = await db.execute(stmt)
    row = result.one()

    return {
        "total_spent": row.total_spent or 0,
        "total_purchases": row.total_purchases or 0,
        "average_price": round(row.average_price,2) if row.average_price else 0
    }

@router.get("/most_expensive")
async def most_expensive(
    num : Optional[int] = Query(5, ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
    ):

    stmt = select(Perfume.name, Perfume.brand, Purchase.price, Purchase.date).\
        join(Purchase, Perfume.id == Purchase.perfume_id).\
        where(Purchase.user_id == current_user.id).\
        order_by(desc(Purchase.price)).\
        limit(num)
    result = await db.execute(stmt)
    most_expensive = result.all()

    
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