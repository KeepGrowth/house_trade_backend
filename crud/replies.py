from typing import List, Optional
from utils.sql import *
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.base import Replies


# 查询帖子
async def query_replies(
        db: AsyncSession,
        query_params: dict
):
    list_stmt = (select(Replies).where(Replies.status == 1))
    total_stmt = select(func.count(Replies.reply_id)).where(Replies.status == 1)
    return await common_query_list(db, query_params, total_stmt, list_stmt, Replies)


# 查询详情
async def get_replies_by_id(
        db: AsyncSession,
        reply_id: int
):
    stmt = (select(Replies).where(Replies.reply_id == reply_id))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# 新增
async def add_replies(
        db: AsyncSession,
        replies: dict,
):
    new_replies = Replies(**replies)
    db.add(new_replies)
    await db.commit()
    await db.refresh(new_replies)
    return new_replies


# 更新
async def update_replies(
        db: AsyncSession,
        replies: dict,
):
    replies = await get_replies_by_id(db, replies.get('reply_id'))
    if not replies:
        return False
    update_stmt = update(Replies).where(Replies.reply_id == replies.reply_id).values(**replies)
    await db.execute(update_stmt)
    await db.commit()
    await db.refresh(replies)
    return replies


# 删除
async def delete_replies(
        db: AsyncSession,
        reply_id: int,
):
    replies = await get_replies_by_id(db, reply_id)
    if not replies:
        return False
    stmt = delete(Replies).where(Replies.reply_id == reply_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0
