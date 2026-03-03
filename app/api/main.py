from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import users, groups, mailings, menu
from app.bot.webhook import webhook_router, setup_webhook
from app.admin.main import admin_app
import app.bot.main  # Import bot config to register middleware/routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    import asyncio
    # Run webhook setup in background so it doesn't block startup
    asyncio.create_task(setup_webhook())
    yield


app = FastAPI(title="Dental Clinic Bot API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/admin", admin_app)

app.include_router(webhook_router)
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(groups.router, prefix="/api/groups", tags=["groups"])
app.include_router(mailings.router, prefix="/api/mailings", tags=["mailings"])
app.include_router(menu.router, prefix="/api/menu", tags=["menu"])
