from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.database import get_db, AsyncSessionLocal
from app.models.models import Mailing, User, UserGroup
from app.services.notifications import send_mailing

router = APIRouter()


class MailingResponse(BaseModel):
    id: int
    title: str
    content: str
    media_path: Optional[str]
    buttons_json: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class MailingCreate(BaseModel):
    title: str
    content: str
    media_path: Optional[str] = None
    buttons_json: Optional[str] = None


class MailingSend(BaseModel):
    group_id: Optional[int] = None
    all_users: bool = False


async def run_mailing_task(mailing_id: int, group_id: Optional[int], send_to_all: bool):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Mailing).where(Mailing.id == mailing_id))
        mailing = result.scalars().first()
        if not mailing:
            return

        query = select(User).where(User.is_active == True)
        if not send_to_all and group_id:
            query = query.join(UserGroup).where(UserGroup.group_id == group_id)
        elif not send_to_all:
            return

        result = await db.execute(query)
        users = result.scalars().all()

        content = mailing.content if mailing.content else ""
        media_path = mailing.media_path if mailing.media_path else None
        buttons_json = mailing.buttons_json if mailing.buttons_json else None

        await send_mailing(db, users, content, media_path, buttons_json)


@router.get("/", response_model=List[MailingResponse])
async def get_mailings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Mailing).order_by(Mailing.created_at.desc()))
    return result.scalars().all()


@router.post("/", response_model=MailingResponse)
async def create_mailing(data: MailingCreate, db: AsyncSession = Depends(get_db)):
    mailing = Mailing(
        title=data.title,
        content=data.content,
        media_path=data.media_path,
        buttons_json=data.buttons_json,
    )
    db.add(mailing)
    await db.commit()
    await db.refresh(mailing)
    return mailing


@router.post("/{mailing_id}/send")
async def send_mailing_endpoint(
    mailing_id: int,
    data: MailingSend,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Mailing).where(Mailing.id == mailing_id))
    mailing = result.scalars().first()
    if not mailing:
        raise HTTPException(status_code=404, detail="Mailing not found")

    background_tasks.add_task(
        run_mailing_task, mailing_id, data.group_id, data.all_users
    )

    return {"message": "Mailing started"}
