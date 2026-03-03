from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.models.models import User, UserGroup

router = APIRouter()


class UserResponse(BaseModel):
    id: int
    telegram_id: Optional[str]
    full_name: Optional[str]
    username: Optional[str]
    phone: Optional[str]
    is_active: bool
    source: Optional[str]
    form_name: Optional[str]
    utm_source: Optional[str]
    utm_medium: Optional[str]
    utm_campaign: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    is_active: Optional[bool] = None


@router.get("/", response_model=List[UserResponse])
async def get_users(
    source: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    group_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    query = select(User)

    if source:
        query = query.where(User.source == source)
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    if group_id:
        query = query.join(UserGroup).where(UserGroup.group_id == group_id)

    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}")
async def update_user(user_id: int, data: UserUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.is_active is not None:
        user.is_active = data.is_active

    await db.commit()
    return {"success": True}


@router.get("/stats/summary")
async def get_stats(db: AsyncSession = Depends(get_db)):
    total_result = await db.execute(select(func.count(User.id)))
    total = total_result.scalar()

    active_result = await db.execute(select(func.count(User.id)).where(User.is_active == True))
    active = active_result.scalar()

    phone_result = await db.execute(select(func.count(User.id)).where(User.phone.isnot(None)))
    with_phone = phone_result.scalar()

    return {"total": total, "active": active, "with_phone": with_phone}
