from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.routers import perfumes, purchases, stats, auth, admin, views

app = FastAPI(
    title="Perfume Tracker",
    version="0.1.0",
    description="Track my perfume collection and purchases"
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def root():
    return RedirectResponse(url="/app/login")

app.include_router(views.router)
app.include_router(auth.router)
app.include_router(perfumes.router)
app.include_router(purchases.router)
app.include_router(stats.router)
app.include_router(admin.router)