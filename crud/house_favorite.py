# ------------------------------
# CRUD 核心方法
# ------------------------------
from typing import Optional, List

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models.house_favorite import Favorite
from schemas.house_favorite import FavoriteCreate


# 1. 添加收藏
async def create_favorite(db: AsyncSession, favorite_in: FavoriteCreate) -> Favorite:
    # 检查是否已收藏（未取消）
    exist = await get_user_favorite(db, user_id=favorite_in.user_id, house_id=favorite_in.house_id)
    if exist:
        # 若已收藏但被取消，则恢复
        if exist.is_deleted == 1:
            exist.is_deleted = 0
            await db.commit()
            await db.refresh(exist)
            return exist
        # 已收藏
        return exist

    db_fav = Favorite(**favorite_in.model_dump())
    db.add(db_fav)
    await db.commit()
    await db.refresh(db_fav)
    return db_fav


# 2. 查询用户是否收藏某房源
async def get_user_favorite(
        db: AsyncSession,
        user_id: int,
        house_id: int
) -> Optional[Favorite]:
    result = await db.execute(
        select(Favorite)
        .where(
            and_(
                Favorite.user_id == user_id,
                Favorite.house_id == house_id
            )
        )
    )
    return result.scalar_one_or_none()


# 3. 获取用户所有收藏（未取消的）
async def get_user_favorites(
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 10
) -> List[Favorite]:
    result = await db.execute(
        select(Favorite)
        .where(
            and_(
                Favorite.user_id == user_id,
                Favorite.is_deleted == 0
            )
        )
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


# 4. 取消收藏（软删除）
async def cancel_favorite(
        db: AsyncSession,
        user_id: int,
        house_id: int
) -> bool:
    fav = await get_user_favorite(db, user_id, house_id)
    if not fav:
        return False

    fav.is_deleted = 1
    await db.commit()
    return True


# 5. 获取房源被收藏次数
async def get_favorite_count(db: AsyncSession, house_id: int) -> int:
    from sqlalchemy import func
    result = await db.execute(
        select(func.count(Favorite.favorite_id))
        .where(
            and_(
                Favorite.house_id == house_id,
                Favorite.is_deleted == 0
            )
        )
    )
    return result.scalar() or 0
