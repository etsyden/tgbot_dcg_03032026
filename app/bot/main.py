from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import get_settings
from app.bot.handlers import router
from app.bot.middleware import DbSessionMiddleware

settings = get_settings()

bot = Bot(
    token=settings.TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Setup middleware and routers immediately
dp.update.outer_middleware(DbSessionMiddleware())
dp.include_router(router)
