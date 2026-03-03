import json
import base64
import asyncio
from aiogram import Router, F
from aiogram.types import Message, Contact
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import User
from app.bot.keyboards import get_main_menu_builder
from app.services.bitrix import create_bitrix_lead
from app.services.notifications import notify_admin

router = Router()

class UserStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_name = State()

def parse_start_param(param: str) -> dict:
    if not param:
        return {}
    try:
        # Try base64 first
        decoded = base64.b64decode(param).decode("utf-8")
        return json.loads(decoded)
    except Exception:
        # Fallback to direct source string
        return {"source": param}

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext, db: AsyncSession):
    start_param = (
        message.text.split(" ", 1)[1] if len(message.text.split(" ", 1)) > 1 else ""
    )
    params = parse_start_param(start_param)

    # Use async select
    result = await db.execute(select(User).where(User.telegram_id == str(message.from_user.id)))
    user = result.scalars().first()

    if not user:
        user = User(
            telegram_id=str(message.from_user.id),
            full_name=message.from_user.full_name,
            username=message.from_user.username,
            source=params.get("source"),
            form_name=params.get("form_name"),
            utm_source=params.get("utm_source"),
            utm_medium=params.get("utm_medium"),
            utm_campaign=params.get("utm_campaign"),
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        # Notify admin (async)
        asyncio.create_task(notify_admin(db, user))

    keyboard = await get_main_menu_builder(db)
    await message.answer(
        "Добро пожаловать в стоматологическую клинику Dental Group!\n\nВыберите нужный пункт меню:",
        reply_markup=keyboard,
    )

@router.message(Command("menu"))
async def cmd_menu(message: Message, db: AsyncSession):
    keyboard = await get_main_menu_builder(db)
    await message.answer("Главное меню:", reply_markup=keyboard)

@router.message(F.contact)
async def handle_contact(message: Message, db: AsyncSession):
    phone = message.contact.phone_number
    result = await db.execute(select(User).where(User.telegram_id == str(message.from_user.id)))
    user = result.scalars().first()

    if user:
        user.phone = phone
        await db.commit()
        # Fire and forget lead creation to not block the bot
        asyncio.create_task(create_bitrix_lead(user))
        await message.answer("Спасибо! Мы свяжемся с вами в ближайшее время.")
    else:
        await message.answer("Пожалуйста, сначала нажмите /start")

@router.message(F.text == "Получить консультацию")
async def get_consultation(message: Message, state: FSMContext):
    await message.answer(
        "Пожалуйста, поделитесь вашим номером телефона:",
        reply_markup={
            "keyboard": [
                [{"text": "Отправить номер телефона", "request_contact": True}]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": True
        },
    )
    await state.set_state(UserStates.waiting_for_phone)

@router.message(F.text == "Позвонить в клинику")
async def call_clinic(message: Message):
    from app.config import get_settings
    settings = get_settings()
    await message.answer(f"Телефон клиники: {settings.CLINIC_PHONE}")

@router.message(F.text == "Наш адрес")
async def location(message: Message):
    from app.config import get_settings
    settings = get_settings()
    await message.answer(f"Мы находимся по адресу: {settings.CLINIC_ADDRESS}")
