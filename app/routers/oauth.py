from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from urllib.parse import urlencode

from app.database import get_db
from app.models import User, OAuthIdentity
from app.auth.oauth import (
    GOOGLE_AUTH_URL,
    GOOGLE_TOKEN_URL,
    GOOGLE_USERINFO_URL,
    create_link_token,
    decode_link_token
)
from app.auth import select, verify_password, create_user_token
from app.config import settings

router = APIRouter(prefix="/oauth", tags=["OAuth"])

@router.get("/auth/callback")
async def google_callback_alias(code: str, db: AsyncSession = Depends(get_db)):
    return await google_callback(code, db)

@router.get("/google")
async def google_login():
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url=url)

@router.get("/callback")
async def google_callback(code: str, db: AsyncSession = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            },
        )
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")
        tokens = token_response.json()
        access_token = tokens.get("access_token")
        userinfo_response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if userinfo_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info from Google")
        google_user = userinfo_response.json()

    google_sub = google_user.get("sub")
    google_email = google_user.get("email")
    google_name = google_user.get("name")
    google_picture = google_user.get("picture")
    email_verified = google_user.get("email_verified", False)

    stmt = select(OAuthIdentity).where(
        OAuthIdentity.provider == "google",
        OAuthIdentity.provider_sub == google_sub
    )
    result = await db.execute(stmt)
    oauth_identity = result.scalars().first()

    if oauth_identity:
        stmt = select(User).where(User.id == oauth_identity.user_id)
        result = await db.execute(stmt)
        user = result.scalars().first()
        token = create_user_token(user)["access_token"]
        return RedirectResponse(url=f"/app/oauth-success?token={token}")

    stmt = select(User).where(User.email == google_email)
    result = await db.execute(stmt)
    existing_user = result.scalars().first()

    if existing_user:
        link_token = create_link_token("google", google_sub, google_email, google_name)
        return RedirectResponse(url=f"/app/oauth-link?link_token={link_token}&email={google_email}&provider=google")

    user = User(
        email=google_email,
        email_verified=email_verified,
        name=google_name,
        avatar_url=google_picture,
        hashed_password=None,
        is_active=True
    )
    db.add(user)
    await db.flush()

    oauth_identity = OAuthIdentity(
        user_id=user.id,
        provider="google",
        provider_sub=google_sub,
        provider_email=google_email
    )
    db.add(oauth_identity)
    await db.commit()
    await db.refresh(user)

    token = create_user_token(user)["access_token"]
    return RedirectResponse(url=f"/app/oauth-success?token={token}")

@router.post("/link")
async def link_oauth_account(link_request, db: AsyncSession = Depends(get_db)):
    payload = decode_link_token(link_request.link_token)
    provider = payload.get("provider")
    provider_sub = payload.get("provider_sub")
    token_email = payload.get("email")
    if link_request.email != token_email:
        raise HTTPException(status_code=400, detail="Email mismatch")
    stmt = select(User).where(User.email == link_request.email)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_oauth_user:
        raise HTTPException(status_code=400, detail="Cannot link OAuth to an OAuth-only account. Account type must be local.")
    if not verify_password(link_request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    stmt = select(OAuthIdentity).where(
        OAuthIdentity.provider == provider,
        OAuthIdentity.provider_sub == provider_sub
    )
    result = await db.execute(stmt)
    existing_identity = result.scalars().first()
    if existing_identity:
        raise HTTPException(status_code=400, detail="This OAuth account is already linked to another user")
    oauth_identity = OAuthIdentity(
        user_id=user.id,
        provider=provider,
        provider_sub=provider_sub,
        provider_email=token_email
    )
    db.add(oauth_identity)
    await db.commit()
    return create_user_token(user)
