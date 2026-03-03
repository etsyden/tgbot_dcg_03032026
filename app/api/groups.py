from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel
from typing import List

from app.database import get_db
from app.models.models import Group, UserGroup

router = APIRouter()


class GroupResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class GroupCreate(BaseModel):
    name: str


@router.get("/", response_model=List[GroupResponse])
async def get_groups(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Group))
    return result.scalars().all()


@router.post("/", response_model=GroupResponse)
async def create_group(data: GroupCreate, db: AsyncSession = Depends(get_db)):
    group = Group(name=data.name)
    db.add(group)
    await db.commit()
    await db.refresh(group)
    return group


@router.delete("/{group_id}")
async def delete_group(group_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Group).where(Group.id == group_id))
    group = result.scalars().first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    await db.execute(delete(UserGroup).where(UserGroup.group_id == group_id))
    await db.delete(group)
    await db.commit()
    return {"success": True}


@router.post("/{group_id}/users/{user_id}")
async def add_user_to_group(group_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UserGroup)
        .where(UserGroup.user_id == user_id, UserGroup.group_id == group_id)
    )
    existing = result.scalars().first()

    if existing:
        return {"error": "User already in group"}

    user_group = UserGroup(user_id=user_id, group_id=group_id)
    db.add(user_group)
    await db.commit()
    return {"success": True}


@router.delete("/{group_id}/users/{user_id}")
async def remove_user_from_group(group_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    await db.execute(
        delete(UserGroup)
        .where(UserGroup.user_id == user_id, UserGroup.group_id == group_id)
    )
    await db.commit()
    return {"success": True}
