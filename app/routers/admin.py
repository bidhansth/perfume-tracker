from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import get_db
from app.models import User, Perfume, Purchase
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
    total_users: int = db.query(func.count(User.id)).scalar()
    total_perfumes: int = db.query(func.count(Perfume.id)).scalar()
    total_purchases: int = db.query(func.count(Purchase.id)).scalar()
    total_amount: float = db.query(func.coalesce(func.sum(Purchase.price), 0.0)).scalar()
    active_users: int = db.query(func.count(User.id)).filter(User.is_active == True).scalar()

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
    most_perfumes_counts = db.query(User, func.count(Perfume.id).label("perfume_count")).\
        join(Perfume, User.id == Perfume.user_id).\
        group_by(User.id).\
        order_by(desc("perfume_count")).\
        limit(limit).all()
    
    most_expensive_perfume = db.query(Purchase, Perfume, User).\
        join(Perfume, Purchase.perfume_id == Perfume.id).\
        join(User, Purchase.user_id == User.id).\
        order_by(desc(Purchase.price)).\
        limit(limit).all()

    most_expensive_collection = db.query(User, func.sum(Purchase.price).label("total_spent")).\
        join(Purchase, User.id == Purchase.user_id).\
        group_by(User.id).\
        order_by(desc("total_spent")).\
        limit(limit).all()

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