from typing import List, Optional

from fastapi import Body
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from crud.users import get_user_by_id
from models.base import Orders
from utils import sql
from utils.sql import common_query_list


# 新增
async def add_orders(
        db: AsyncSession,
        orders: dict,
):
    """
    新增订单
    :param db:
    :param orders:
    :return:
    """
    orders = Orders(
        **orders,
    )
    db.add(orders)
    await db.commit()
    await db.refresh(orders)
    return orders


# 更新
async def update_orders(
        db: AsyncSession,
        orders: dict,
):
    return await sql.update_by_id(db, Orders, orders.get('id'), orders)


# 条件查询
async def query_orders(
        db: AsyncSession,
        query_params: dict,
):
    list_stmt = select(Orders)
    total_stmt = select(func.count(Orders.id))
    return await common_query_list(db, query_params, total_stmt, list_stmt, Orders)


# 删除
async def del_order(
        db: AsyncSession,
        order_id: int,
):
    return await sql.delete_by_id(db, Orders, order_id)


# 获取单条
async def get_order_by_id(
        db: AsyncSession,
        order_id: int,
):
    return await sql.get_by_id(db, Orders, order_id)
