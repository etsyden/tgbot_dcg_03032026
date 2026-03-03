from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import bcrypt
import os
from sqlalchemy import select, func

from app.config import get_settings
from app.database import AsyncSessionLocal
from app.models.models import User, Group, Mailing, MenuItem

settings = get_settings()
security = HTTPBasic()

admin_app = FastAPI(title="Dental Clinic Admin")

static_dir = os.path.join(os.path.dirname(__file__), "static")
templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "templates")
)

if os.path.exists(static_dir):
    admin_app.mount("/static", StaticFiles(directory=static_dir), name="static")


async def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != settings.ADMIN_USERNAME:
        raise HTTPException(status_code=401, detail="Invalid credentials", headers={"WWW-Authenticate": "Basic"})

    # The hashed password should be stored in ADMIN_PASSWORD in .env
    # For now, if it starts with $2b$, we assume it's hashed.
    # Otherwise, we might need a plain text fallback for initial setup (not recommended)
    is_valid = False
    try:
        if settings.ADMIN_PASSWORD.startswith("$2"):
            if bcrypt.checkpw(
                credentials.password.encode(), settings.ADMIN_PASSWORD.encode()
            ):
                is_valid = True
        else:
            if credentials.password == settings.ADMIN_PASSWORD:
                is_valid = True
    except Exception:
        if credentials.password == settings.ADMIN_PASSWORD:
            is_valid = True

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid credentials", headers={"WWW-Authenticate": "Basic"})

    return credentials


@admin_app.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request, credentials: HTTPBasicCredentials = Depends(verify_credentials)
):
    async with AsyncSessionLocal() as db:
        total_users_res = await db.execute(select(func.count(User.id)))
        total_users = total_users_res.scalar()
        
        active_users_res = await db.execute(select(func.count(User.id)).where(User.is_active == True))
        active_users = active_users_res.scalar()
        
        total_groups_res = await db.execute(select(func.count(Group.id)))
        total_groups = total_groups_res.scalar()
        
        total_mailings_res = await db.execute(select(func.count(Mailing.id)))
        total_mailings = total_mailings_res.scalar()

        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "total_users": total_users,
                "active_users": active_users,
                "total_groups": total_groups,
                "total_mailings": total_mailings,
                "prefix": "/admin" # We will use this in templates if needed, or just hardcode /admin/
            },
        )


@admin_app.get("/users", response_class=HTMLResponse)
async def users_page(
    request: Request, credentials: HTTPBasicCredentials = Depends(verify_credentials)
):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).order_by(User.created_at.desc()).limit(100))
        users = result.scalars().all()
        return templates.TemplateResponse(
            "users.html", {"request": request, "users": users}
        )


@admin_app.get("/groups", response_class=HTMLResponse)
async def groups_page(
    request: Request, credentials: HTTPBasicCredentials = Depends(verify_credentials)
):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Group))
        groups = result.scalars().all()
        return templates.TemplateResponse(
            "groups.html", {"request": request, "groups": groups}
        )


@admin_app.get("/mailings", response_class=HTMLResponse)
async def mailings_page(
    request: Request, credentials: HTTPBasicCredentials = Depends(verify_credentials)
):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Mailing).order_by(Mailing.created_at.desc()))
        mailings = result.scalars().all()
        return templates.TemplateResponse(
            "mailings.html", {"request": request, "mailings": mailings}
        )


@admin_app.get("/menu", response_class=HTMLResponse)
async def menu_page(
    request: Request, credentials: HTTPBasicCredentials = Depends(verify_credentials)
):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(MenuItem).order_by(MenuItem.position))
        menu_items = result.scalars().all()
        return templates.TemplateResponse(
            "menu.html", {"request": request, "menu_items": menu_items}
        )
