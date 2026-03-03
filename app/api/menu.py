from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List

from app.database import get_db
from app.models.models import MenuItem

router = APIRouter()


class MenuItemResponse(BaseModel):
    id: int
    name: str
    url: Optional[str]
    position: int
    is_active: bool

    class Config:
        from_attributes = True


class MenuItemCreate(BaseModel):
    name: str
    url: Optional[str] = None
    position: int = 0


class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    position: Optional[int] = None
    is_active: Optional[bool] = None


@router.get("/", response_model=List[MenuItemResponse])
async def get_menu_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MenuItem).order_by(MenuItem.position))
    return result.scalars().all()


@router.post("/", response_model=MenuItemResponse)
async def create_menu_item(data: MenuItemCreate, db: AsyncSession = Depends(get_db)):
    item = MenuItem(
        name=data.name, url=data.url, position=data.position, is_active=True
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.patch("/{item_id}", response_model=MenuItemResponse)
async def update_menu_item(item_id: int, data: MenuItemUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MenuItem).where(MenuItem.id == item_id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if data.name is not None:
        item.name = data.name
    if data.url is not None:
        item.url = data.url
    if data.position is not None:
        item.position = data.position
    if data.is_active is not None:
        item.is_active = data.is_active

    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{item_id}")
async def delete_menu_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MenuItem).where(MenuItem.id == item_id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    await db.delete(item)
    await db.commit()
    return {"success": True}
