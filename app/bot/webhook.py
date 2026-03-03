from aiogram import Router
from aiogram.types import Update
from fastapi import APIRouter, Request, HTTPException, Header
from app.bot.main import bot, dp
from app.bot.handlers import router
from app.config import get_settings
from typing import Optional

settings = get_settings()
webhook_router = APIRouter()

# Don't create a new Dispatcher here, use the one from app.bot.main
# dp.include_router(router) is handled in app/main.py or here once

async def verify_webhook_secret(
    x_telegram_bot_api_secret_token: Optional[str] = Header(None),
):
    if settings.WEBHOOK_SECRET:
        if not x_telegram_bot_api_secret_token:
            raise HTTPException(status_code=401, detail="Missing secret token")
        if x_telegram_bot_api_secret_token != settings.WEBHOOK_SECRET:
            raise HTTPException(status_code=401, detail="Invalid secret token")


@webhook_router.post("/webhook")
async def telegram_webhook(
    request: Request, x_telegram_bot_api_secret_token: Optional[str] = Header(None)
):
    if settings.WEBHOOK_SECRET:
        if not x_telegram_bot_api_secret_token:
            raise HTTPException(status_code=401, detail="Missing secret token")
        if x_telegram_bot_api_secret_token != settings.WEBHOOK_SECRET:
            raise HTTPException(status_code=401, detail="Invalid secret token")

    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot=bot, update=update)
    return {"ok": True}


async def setup_webhook():
    if settings.WEBHOOK_URL:
        # Ensure router is included before setting up webhook if not already
        if router not in dp.sub_routers:
             dp.include_router(router)
             
        await bot.set_webhook(
            url=f"{settings.WEBHOOK_URL.rstrip('/')}/webhook",
            secret_token=settings.WEBHOOK_SECRET if settings.WEBHOOK_SECRET else None,
        )
        print(f"Webhook set to {settings.WEBHOOK_URL.rstrip('/')}/webhook")
    else:
        print("WEBHOOK_URL not set, using polling mode")
