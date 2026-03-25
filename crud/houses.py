from typing import List, Optional

from fastapi import Body
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from crud.users import get_user_by_id
from models.base import House, Review


# 条件查询获取房源列表
async def get_houses(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        params: dict = None
):
    """
    条件查询获取房源列表
    :param db:
    :param page:
    :param page_size:
    :param params:
    :return:
    """
    page = max(page, 1)
    page_size = max(page_size, 1)
    query = (
        select(House)
        .options(selectinload(House.images))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    if params:
        query = query.where(House.house_id == params.get("house_id"))
        query = query.where(House.district == params.get("district"))
        query = query.where(House.house_type == params.get("house_type"))
    if params.get('order_by'):
        query = query.order_by(params.get('order_by'))
    if params.get('max_price') and params.get('min_price'):
        query = query.where(House.price >= params.get('min_price'))
        query = query.where(House.price <= params.get('max_price'))
    houses = await db.execute(query.options(selectinload(House.images)))
    return houses.scalars().all()


# 获取单个房源信息
async def get_house_by_id(
        db: AsyncSession,
        house_id: int
):
    """
    获取单个房源信息
    :param db:
    :param house_id:
    :return:
    """
    query = select(House).where(House.house_id == house_id)
    house = await db.execute(query)
    return house.scalars().first()


# 新增房源
async def create_house(
        db: AsyncSession,
        house: dict,
        user_id: int
):
    """
    新增房源
    :param db:
    :param house:
    :param user_id:
    :return:
    """
    house = House(
        **house,
        user_id=user_id
    )
    db.add(house)
    await db.commit()
    await db.refresh(house)
    return house


# 删除单个房源
async def delete_house(
        db: AsyncSession,
        house_id: Body(None, title="房源ID", alias="houseId")
):
    """
    删除单个房源
    :param db:
    :param house_id:
    :return:
    """
    house = await get_house_by_id(db, house_id)
    await db.delete(house)
    await db.commit()
    return house


# 获取某个用户的房源列表
async def get_user_houses(
        db: AsyncSession,
        user_id: int
):
    """
    获取某个用户的房源列表
    :param db:
    :param user_id:
    :return:
    """
    query = select(House).where(House.user_id == user_id)
    houses = await db.execute(query)
    return houses.scalars().all()
