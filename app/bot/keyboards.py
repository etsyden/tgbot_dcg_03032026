from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import MenuItem


async def get_main_menu_keyboard(db: AsyncSession) -> InlineKeyboardMarkup:
    result = await db.execute(
        select(MenuItem)
        .where(MenuItem.is_active == True)
        .order_by(MenuItem.position)
    )
    menu_items = result.scalars().all()

    buttons = []
    for item in menu_items:
        buttons.append([InlineKeyboardButton(text=item.name, url=item.url)])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def get_main_menu_builder(db: AsyncSession):
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    result = await db.execute(
        select(MenuItem)
        .where(MenuItem.is_active == True)
        .order_by(MenuItem.position)
    )
    menu_items = result.scalars().all()

    builder = InlineKeyboardBuilder()
    for item in menu_items:
        builder.add(InlineKeyboardButton(text=item.name, url=item.url))

    builder.adjust(1)
    return builder.as_markup()
