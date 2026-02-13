from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.routers import perfumes, purchases, stats, auth, admin, views, oauth
from app.config import settings

app = FastAPI(
    title="Perfume Tracker",
    version="0.1.0",
    description="Track my perfume collection and purchases"
)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.JWT_SECRET_KEY,
    session_cookie="session",
    max_age=1800,
    same_site="lax",
    https_only=False,
    # path="/"
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def root():
    return RedirectResponse(url="/app/login")

app.include_router(views.router)
app.include_router(auth.router)
app.include_router(perfumes.router)
app.include_router(purchases.router)
app.include_router(stats.router)
app.include_router(admin.router)
app.include_router(oauth.router)