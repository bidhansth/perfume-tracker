from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date

from app.auth import get_current_active_user
from app.database import get_db
from app.models import Purchase, Perfume, User
from app.schemas import PurchaseCreate, PurchaseRead, PaginatedResponse

router = APIRouter(prefix="/purchases", tags=["Purchases"])

@router.post("", response_model=PurchaseRead, status_code=status.HTTP_201_CREATED)
async def create_purchase(
    purchase_in: PurchaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
    ):
    stmt = select(Perfume).where(Perfume.id == purchase_in.perfume_id)
    result = await db.execute(stmt)
    perfume = result.scalars().first()

    if not perfume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfume not found")

    if perfume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this perfume"
        )

    purchase = Purchase(
        perfume_id=purchase_in.perfume_id,
        user_id=current_user.id,
        date=purchase_in.date,
        price=purchase_in.price,
        store=purchase_in.store,
        ml=purchase_in.ml,
    )

    db.add(purchase)
    await db.commit()
    await db.refresh(purchase)

    return purchase

@router.get("", response_model=PaginatedResponse[PurchaseRead])
async def list_purchases(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
    ):

    stmt = select(Purchase).where(Purchase.user_id == current_user.id)

    if start_date:
        stmt = stmt.where(Purchase.date >= start_date)
    if end_date:
        stmt = stmt.where(Purchase.date <= end_date)
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start date cannot be after end date")
    
    if min_price is not None:
        stmt = stmt.where(Purchase.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(Purchase.price <= max_price)
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Minimum price cannot be greater than maximum price")
    
    total_stmt = select(func.count()).select_from(stmt.subquery())
    result = await db.execute(total_stmt)
    total = result.scalar_one()

    result = await db.execute(stmt.offset(offset).limit(limit))
    items = result.scalars().all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items
    }

@router.get("/{purchase_id}", response_model=PurchaseRead)
async def get_purchase(
    purchase_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
    ):
    stmt = select(Purchase).where(Purchase.id == purchase_id)
    result = await db.execute(stmt)
    purchase = result.scalar_one_or_none()

    if not purchase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase not found")

    if purchase.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this purchase"
        )
    return purchase

@router.delete("/{purchase_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_purchase(
    purchase_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
    ):
    stmt = select(Purchase).where(Purchase.id == purchase_id)
    result = await db.execute(stmt)
    purchase = result.scalar_one_or_none()

    if not purchase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase not found")

    if purchase.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this purchase"
        )
    
    await db.delete(purchase)
    await db.commit()

    return purchase
