from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional, List, Generic, TypeVar, Dict
from .models import Concentration, Role, Season
from datetime import date, datetime

class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Email address")
    name: Optional[str] = None
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password min 6 characters")

class UserRead(UserBase):
    id: int
    role: Role
    is_active: bool
    created_at: datetime
    is_oauth_user: bool = False

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    role: Optional[Role] = None
    is_active: Optional[bool] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class OAuthIdentityResponse(BaseModel):
    id: int
    provider: str
    provider_sub: str
    provider_email: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class OAuthLinkRequest(BaseModel):
    """Request to link OAuth to existing account."""
    email: EmailStr
    password: str
    link_token: str

class OAuthLinkResponse(BaseModel):
    """Response when email conflict detected during OAuth."""
    message: str
    email: EmailStr
    provider: str
    link_token: str

class SetPassword(BaseModel):
    """Request to set password for OAuth-only user."""
    password: str = Field(..., min_length=6, description="Password min 6 characters")

class PerfumeBase(BaseModel):
    name: str
    brand: str
    concentration: Concentration
    season : Season
    available: bool = True

class PerfumeCreate(PerfumeBase):
    pass

class PerfumeRead(PerfumeBase):
    id: int
    user_id: int
    
    model_config = ConfigDict(from_attributes=True)

class PerfumeReadAdmin(PerfumeRead):
    owner: UserRead

    model_config = ConfigDict(from_attributes=True)

class PerfumeList(BaseModel):
    items: List[PerfumeRead]
    total: int

# purchase schemas

class PurchaseBase(BaseModel):
    perfume_id: int
    date: date
    price: float
    store: str
    ml: int = 100

class PurchaseCreate(PurchaseBase):
    pass

class PurchaseRead(PurchaseBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)

class PurchaseReadAdmin(PurchaseRead):
    user: UserRead
    perfume: PerfumeRead

    model_config = ConfigDict(from_attributes=True)

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    limit: int
    offset: int
    items: List[T]

class AdminDashboard(BaseModel):
    total_users: int
    total_perfumes: int
    total_purchases: int
    total_amount: float
    active_users: int

class UserPerfumeCount(BaseModel):
    perfume_count: int
    user: UserRead
    
    model_config = ConfigDict(from_attributes=True)

class MostExpensivePurchase(BaseModel):
    price: float
    perfume: PerfumeRead
    user: UserRead
    
    model_config = ConfigDict(from_attributes=True)

class UserTotalSpent(BaseModel):
    total_spent: float
    user: UserRead
    
    model_config = ConfigDict(from_attributes=True)

class TopUsersResponse(BaseModel):
    most_perfumes: Optional[List[UserPerfumeCount]]
    most_expensive_purchase: Optional[List[MostExpensivePurchase]]
    most_expensive_collection: Optional[List[UserTotalSpent]]
