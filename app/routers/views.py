from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/app", tags=["Views"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/perfumes")
def perfumes_page(request: Request):
    return templates.TemplateResponse("perfumes.html", {"request": request})


@router.get("/perfumes/add")
def add_perfume_page(request: Request):
    return templates.TemplateResponse("add_perfume.html", {"request": request})


@router.get("/purchases")
def purchases_page(request: Request):
    return templates.TemplateResponse("purchases.html", {"request": request})


@router.get("/purchases/add")
def add_purchase_page(request: Request):
    return templates.TemplateResponse("add_purchase.html", {"request": request})


@router.get("/stats")
def stats_page(request: Request):
    return templates.TemplateResponse("stats.html", {"request": request})


# Admin routes
@router.get("/admin")
def admin_dashboard_page(request: Request):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})


@router.get("/admin/users")
def admin_users_page(request: Request):
    return templates.TemplateResponse("admin_users.html", {"request": request})


@router.get("/admin/top-users")
def admin_top_users_page(request: Request):
    return templates.TemplateResponse("admin_top_users.html", {"request": request})
