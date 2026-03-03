import asyncio
import logging
from app.bot.main import dp, bot
from app.bot.handlers import router
from app.bot.webhook import setup_webhook
from app.bot.middleware import DbSessionMiddleware
from app.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


async def main():
    # Setup middleware if not already added
    if not any(isinstance(m, DbSessionMiddleware) for m in dp.update.outer_middleware):
        dp.update.middleware(DbSessionMiddleware())
    
    # Safely include router
    if router not in dp.sub_routers:
        dp.include_router(router)

    try:
        if settings.WEBHOOK_URL:
            await setup_webhook()
            # If run as a standalone bot process in webhook mode, 
            # we stay alive to handle any background tasks if they exist
            print("Bot is running in Webhook mode. Waiting for updates via API...")
            await asyncio.Future() 
        else:
            # If in polling mode, we should delete webhook first
            await bot.delete_webhook(drop_pending_updates=True)
            print("Bot is running in Polling mode...")
            await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
