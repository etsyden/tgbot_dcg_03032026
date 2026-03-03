import asyncio
import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import User
from app.config import get_settings
from app.bot.main import bot
from aiogram.types import FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup

settings = get_settings()


async def notify_admin(db: AsyncSession, user: User):
    if not settings.ADMIN_CHAT_ID:
        return

    message = (
        f"🔔 Новый пользователь!\n\n"
        f"Имя: {user.full_name or 'Не указано'}\n"
        f"Username: @{user.username or 'нет'}\n"
        f"Источник: {user.source or 'не указан'}\n"
        f"Форма: {user.form_name or 'не указана'}\n"
        f"UTM: {user.utm_source or '—'}/{user.utm_medium or '—'}/{user.utm_campaign or '—'}"
    )

    try:
        await bot.send_message(settings.ADMIN_CHAT_ID, message)
    except Exception as e:
        print(f"Failed to notify admin: {e}")


async def send_mailing(
    db: AsyncSession,
    users: list[User],
    content: str,
    media_path: str = None,
    buttons_json: str = None,
):
    success_count = 0
    failed_count = 0

    keyboard = None
    if buttons_json:
        try:
            buttons_data = json.loads(buttons_json)
            if buttons_data and isinstance(buttons_data, list):
                keyboard_buttons = []
                for btn in buttons_data:
                    if isinstance(btn, dict) and btn.get("text") and btn.get("url"):
                        keyboard_buttons.append(
                            [InlineKeyboardButton(text=btn["text"], url=btn["url"])]
                        )
                if keyboard_buttons:
                    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        except Exception:
            pass

    for user in users:
        if not user.telegram_id or not user.is_active:
            failed_count += 1
            continue

        try:
            if media_path:
                photo = FSInputFile(media_path)
                await bot.send_photo(
                    user.telegram_id,
                    photo=photo,
                    caption=content,
                    reply_markup=keyboard,
                )
            else:
                await bot.send_message(user.telegram_id, content, reply_markup=keyboard)
            success_count += 1
        except Exception as e:
            failed_count += 1
            print(f"Failed to send to {user.telegram_id}: {e}")

        # Sleep to respect Telegram limits (~30/sec)
        await asyncio.sleep(0.05)

    return {"success": success_count, "failed": failed_count}
