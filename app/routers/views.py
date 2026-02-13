from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/app", tags=["Views"])

templates = Jinja2Templates(directory="app/templates")

@router.get("/oauth-success")
async def oauth_success_page(request: Request):
    return templates.TemplateResponse("oauth_success.html", {"request": request})


@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/perfumes")
async def perfumes_page(request: Request):
    return templates.TemplateResponse("perfumes.html", {"request": request})


@router.get("/perfumes/add")
async def add_perfume_page(request: Request):
    return templates.TemplateResponse("add_perfume.html", {"request": request})


@router.get("/purchases")
async def purchases_page(request: Request):
    return templates.TemplateResponse("purchases.html", {"request": request})


@router.get("/purchases/add")
async def add_purchase_page(request: Request):
    return templates.TemplateResponse("add_purchase.html", {"request": request})


@router.get("/stats")
async def stats_page(request: Request):
    return templates.TemplateResponse("stats.html", {"request": request})


# Admin routes
@router.get("/admin")
async def admin_dashboard_page(request: Request):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})


@router.get("/admin/users")
async def admin_users_page(request: Request):
    return templates.TemplateResponse("admin_users.html", {"request": request})


@router.get("/admin/top-users")
async def admin_top_users_page(request: Request):
    return templates.TemplateResponse("admin_top_users.html", {"request": request})
