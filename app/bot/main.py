from app.bot.bot_instance import bot, dp
from app.bot.handlers import router
from app.bot.middleware import DbSessionMiddleware

# Setup middleware and routers
# This must be done only once. We can do it here as this file is imported by app/main.py
if not any(isinstance(m, DbSessionMiddleware) for m in dp.update.outer_middleware):
    dp.update.outer_middleware(DbSessionMiddleware())

if router not in dp.sub_routers:
    dp.include_router(router)
