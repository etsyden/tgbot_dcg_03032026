from app.bot.bot_instance import bot, dp
from app.bot.handlers import router
from app.bot.middleware import DbSessionMiddleware

# Setup middleware and routers
# We register it directly. aiogram 3 handles multiple registrations gracefully 
# or we can just trust this is called once during startup.
dp.update.outer_middleware(DbSessionMiddleware())
dp.include_router(router)
