from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, select

from app.database import get_db
from app.models import User, Perfume, Purchase, Role
from app.schemas import (
    PerfumeRead,
    UserRead,
    TopUsersResponse,
    AdminDashboard,
    UserPerfumeCount,
    UserTotalSpent,
    MostExpensivePurchase
)
from app.auth import get_current_admin_user

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/stats/dashboard", response_model=AdminDashboard)
def get_admin_dashboard(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
    ):
    total_users: int = db.execute(select(func.count(User.id)).where(User.role != Role.ADMIN)).scalar()
    total_perfumes: int = db.execute(select(func.count(Perfume.id))).scalar()
    total_purchases: int = db.execute(select(func.count(Purchase.id))).scalar()
    total_amount: float = db.execute(select(func.coalesce(func.sum(Purchase.price), 0.0))).scalar()
    active_users: int = db.execute(select(func.count(User.id)).where(User.is_active == True).where(User.role != Role.ADMIN)).scalar()

    return AdminDashboard(
        total_users=total_users or 0,
        total_perfumes=total_perfumes or 0,
        total_purchases=total_purchases or 0,
        total_amount=round(total_amount, 2) if total_amount else 0.0,
        active_users=active_users or 0
    )

@router.get("/stats/top-users", response_model=TopUsersResponse)
def get_top_users(
    limit: int = Query(3, ge=1, le=10, description="Number of top users to return"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
    ):
    most_perfumes_counts = db.execute(
        select(User, func.count(Perfume.id).label("perfume_count"))
        .join(Perfume, User.id == Perfume.user_id)
        .group_by(User.id)
        .order_by(desc("perfume_count"))
        .limit(limit)
    ).all()
    
    most_expensive_perfume = db.execute(
        select(Purchase, Perfume, User)
        .join(Perfume, Purchase.perfume_id == Perfume.id)
        .join(User, Purchase.user_id == User.id)
        .order_by(desc(Purchase.price))
        .limit(limit)
    ).all()

    most_expensive_collection = db.execute(
        select(User, func.sum(Purchase.price).label("total_spent"))
        .join(Purchase, User.id == Purchase.user_id)
        .group_by(User.id)
        .order_by(desc("total_spent"))
        .limit(limit)
    ).all()

    return TopUsersResponse(
        most_perfumes=[
            UserPerfumeCount(
                perfume_count=int(item[1]),
                user=UserRead.model_validate(item[0])
            ) for item in most_perfumes_counts
        ] if most_perfumes_counts else None,
        
        most_expensive_purchase=[
            MostExpensivePurchase(
                price=item[0].price,
                perfume=PerfumeRead.model_validate(item[1]),
                user=UserRead.model_validate(item[2])
            ) for item in most_expensive_perfume
        ] if most_expensive_perfume else None,

        most_expensive_collection=[
            UserTotalSpent(
                total_spent=item[1],
                user=UserRead.model_validate(item[0])
            ) for item in most_expensive_collection
        ] if most_expensive_collection else None
    )


@router.get("/users", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    users = db.execute(select(User)).scalars().all()
    return users


@router.patch("/users/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    user_update: dict,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    
    user = db.execute(select(User).where(User.id == user_id)).scalars().first()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    
    if "is_active" in user_update:
        user.is_active = user_update["is_active"]
    if "role" in user_update:
        user.role = Role(user_update["role"])
    
    db.commit()
    db.refresh(user)
    return user