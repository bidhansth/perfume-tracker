from fastapi import FastAPI
from app.routers import perfumes, purchases

app = FastAPI(
    title="Perfume Tracker",
    version="0.1.0",
    description="Track my perfume collection and purchases"
)

@app.get('/')
def root():
    return {"status": "ok",
            "message": "Perfume Tracker is running"}

app.include_router(perfumes.router)
app.include_router(purchases.router)