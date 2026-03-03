import asyncio
import logging
from app.api.main import app  # Expose app for gunicorn (app.main:app)
from app.bot.bot_instance import dp, bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Fallback runner for polling mode (python -m app.main)"""
    from app.bot.webhook import setup_webhook
    
    # In polling we need to delete webhook first
    await bot.delete_webhook(drop_pending_updates=True)
    print("Bot is running in Polling mode...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
