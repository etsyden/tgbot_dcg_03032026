from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import bcrypt
import os

from app.config import get_settings

settings = get_settings()
security = HTTPBasic()

app = FastAPI(title="Dental Clinic Admin")

static_dir = os.path.join(os.path.dirname(__file__), "static")
templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "templates")
)

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != settings.ADMIN_USERNAME:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not bcrypt.checkpw(
        credentials.password.encode(), settings.ADMIN_PASSWORD.encode()
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return credentials


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request, credentials: HTTPBasicCredentials = Depends(verify_credentials)
):
    from app.database import SessionLocal
    from app.models.models import User, Group, Mailing

    db = SessionLocal()
    try:
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        total_groups = db.query(Group).count()
        total_mailings = db.query(Mailing).count()

        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "total_users": total_users,
                "active_users": active_users,
                "total_groups": total_groups,
                "total_mailings": total_mailings,
            },
        )
    finally:
        db.close()


@app.get("/users", response_class=HTMLResponse)
async def users_page(
    request: Request, credentials: HTTPBasicCredentials = Depends(verify_credentials)
):
    from app.database import SessionLocal
    from app.models.models import User

    db = SessionLocal()
    try:
        users = db.query(User).order_by(User.created_at.desc()).limit(100).all()
        return templates.TemplateResponse(
            "users.html", {"request": request, "users": users}
        )
    finally:
        db.close()


@app.get("/groups", response_class=HTMLResponse)
async def groups_page(
    request: Request, credentials: HTTPBasicCredentials = Depends(verify_credentials)
):
    from app.database import SessionLocal
    from app.models.models import Group

    db = SessionLocal()
    try:
        groups = db.query(Group).all()
        return templates.TemplateResponse(
            "groups.html", {"request": request, "groups": groups}
        )
    finally:
        db.close()


@app.get("/mailings", response_class=HTMLResponse)
async def mailings_page(
    request: Request, credentials: HTTPBasicCredentials = Depends(verify_credentials)
):
    from app.database import SessionLocal
    from app.models.models import Mailing

    db = SessionLocal()
    try:
        mailings = db.query(Mailing).order_by(Mailing.created_at.desc()).all()
        return templates.TemplateResponse(
            "mailings.html", {"request": request, "mailings": mailings}
        )
    finally:
        db.close()


@app.get("/menu", response_class=HTMLResponse)
async def menu_page(
    request: Request, credentials: HTTPBasicCredentials = Depends(verify_credentials)
):
    from app.database import SessionLocal
    from app.models.models import MenuItem

    db = SessionLocal()
    try:
        menu_items = db.query(MenuItem).order_by(MenuItem.position).all()
        return templates.TemplateResponse(
            "menu.html", {"request": request, "menu_items": menu_items}
        )
    finally:
        db.close()
