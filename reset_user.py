import asyncio
import sys
from sqlalchemy import select, delete
from app.database import AsyncSessionLocal
from app.models.models import User, UserGroup

async def reset_user(telegram_id: str):
    async with AsyncSessionLocal() as db:
        # Find user
        result = await db.execute(select(User).where(User.telegram_id == str(telegram_id)))
        user = result.scalars().first()
        
        if not user:
            print(f"❌ Пользователь с ID {telegram_id} не найден в базе.")
            return

        # Delete from groups first (foreign key)
        await db.execute(delete(UserGroup).where(UserGroup.user_id == user.id))
        
        # Delete user
        await db.delete(user)
        await db.commit()
        print(f"✅ Пользователь {user.full_name} (@{user.username}) успешно удален.")
        print("Теперь бот воспримет его как нового при нажатии /start.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python reset_user.py ТЕЛЕГРАМ_ID")
    else:
        asyncio.run(reset_user(sys.argv[1]))
