from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Literal, Optional
from sqlalchemy import asc, desc, func, select

from app.auth import get_current_active_user
from app.database import get_db
from app.models import Perfume, Purchase, User
from app.schemas import PerfumeCreate, PerfumeRead, PurchaseRead, PaginatedResponse

router = APIRouter(prefix="/perfumes", tags=["Perfumes"])

@router.post("", response_model=PerfumeRead, status_code=status.HTTP_201_CREATED)
def create_perfume(
    perfume_in: PerfumeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
    ):
    perfume = Perfume(
        name = perfume_in.name,
        brand = perfume_in.brand,
        concentration = perfume_in.concentration,
        season = perfume_in.season,
        available = perfume_in.available,
        user_id = current_user.id
    )

    db.add(perfume)
    db.commit()
    db.refresh(perfume)
    return perfume

@router.get("", response_model=PaginatedResponse[PerfumeRead])
def list_perfumes(
    available: Optional[bool] = Query(None),
    concentration: Optional[str] = Query(None),
    season: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None, description="Sort by: name, brand"),
    order: Literal["asc", "desc"] = Query("asc"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
    ):

    stmt = select(Perfume).where(Perfume.user_id == current_user.id)

    if available is not None:
        stmt = stmt.where(Perfume.available == available)
    if concentration is not None:
        stmt = stmt.where(Perfume.concentration == concentration)
    if season is not None:
        stmt = stmt.where(Perfume.season == season)
    if brand is not None:
        stmt = stmt.where(Perfume.brand.ilike(f"%{brand}%"))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    allowed_sort_fields = {"name": Perfume.name, "brand": Perfume.brand}
    if sort_by:
        if sort_by not in allowed_sort_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort_by field. Allowed fields are: {', '.join(allowed_sort_fields.keys())}"
            )
        
        column = allowed_sort_fields[sort_by]
        stmt = stmt.order_by(column.asc() if order == "asc" else column.desc())

    stmt = stmt.offset(offset).limit(limit)
    items = db.execute(stmt).scalars().all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items
    }

@router.get("/{perfume_id}", response_model=PerfumeRead)
def get_perfume(
    perfume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
    ):
    perfume = db.query(Perfume).filter(Perfume.id == perfume_id).first()

    if not perfume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfume not found"
        )
    
    if perfume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this perfume"
        )

    return perfume

@router.get("/{perfume_id}/purchases", response_model=List[PurchaseRead])
def get_perfume_purchases(
    perfume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
    ):
    perfume = db.query(Perfume).filter(Perfume.id == perfume_id).first()

    if not perfume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfume not found"
        )

    if perfume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this perfume"
        )

    return perfume.purchases