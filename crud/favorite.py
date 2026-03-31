from typing import List, Optional

from fastapi import Body
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from crud.users import get_user_by_id
from models.base import House, Favorite


# 获取收藏列表
async def get_my_favorites(
        db: AsyncSession,
        user_id: int,
        params: Optional[dict] = None
):
    stmt = select(Favorite).where(Favorite.user_id == user_id).options(
        selectinload(Favorite.house)
        .selectinload(House.images)
    )
    favorites = await db.execute(stmt)
    total = await db.execute(select(func.count(Favorite.favorite_id)))
    total = total.scalar()
    return total, favorites.scalars().all()


# 获取单挑收藏记录
async def get_favorite_by_id(
        db: AsyncSession,
        favorite_id: int
):
    favorite = await db.execute(select(Favorite).where(Favorite.favorite_id == favorite_id))
    return favorite.scalar()


# 删除收藏记录
async def delete_favorite(
        db: AsyncSession,
        favorite_id: int,
        user_id: int
):
    favorite = await get_favorite_by_id(db, favorite_id)
    await db.delete(favorite)
    await db.commit()
    return await get_user_by_id(db, user_id)
