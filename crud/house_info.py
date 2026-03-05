# ------------------------------
# CRUD 方法
# ------------------------------
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.house_info import HouseInfo
from schemas.house_info import *


# 创建房源
async def create_house(db: AsyncSession, house: HouseCreate) -> HouseInfo:
    db_house = HouseInfo(**house.model_dump())
    db.add(db_house)
    await db.commit()
    await db.refresh(db_house)
    return db_house


# 根据ID获取房源
async def get_house_by_id(db: AsyncSession, house_id: int) -> Optional[HouseInfo]:
    result = await db.execute(select(HouseInfo).where(HouseInfo.house_id == house_id))
    return result.scalar_one_or_none()


# 获取用户发布的所有房源
async def get_houses_by_user_id(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 10) -> List[HouseInfo]:
    result = await db.execute(
        select(HouseInfo)
        .where(HouseInfo.user_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


# 分页获取所有房源
async def get_houses(db: AsyncSession, skip: int = 0, limit: int = 10) -> List[HouseInfo]:
    result = await db.execute(select(HouseInfo).offset(skip).limit(limit))
    return result.scalars().all()


# 根据区域/小区筛选（扩展常用）
async def get_houses_by_district_community(
        db: AsyncSession,
        district: Optional[str] = None,
        community: Optional[str] = None,
        skip: int = 0,
        limit: int = 10
) -> List[HouseInfo]:
    query = select(HouseInfo)
    if district:
        query = query.where(HouseInfo.district == district)
    if community:
        query = query.where(HouseInfo.community == community)
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


# 更新房源
async def update_house(db: AsyncSession, house_id: int, house_update: HouseUpdate) -> Optional[HouseInfo]:
    db_house = await get_house_by_id(db, house_id)
    if not db_house:
        return None

    update_data = house_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_house, key, value)

    await db.commit()
    await db.refresh(db_house)
    return db_house


# 删除房源
async def delete_house(db: AsyncSession, house_id: int) -> bool:
    db_house = await get_house_by_id(db, house_id)
    if not db_house:
        return False

    await db.delete(db_house)
    await db.commit()
    return True
