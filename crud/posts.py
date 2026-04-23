from typing import List, Optional
from utils.sql import *
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.base import Posts


# 查询帖子
async def query_posts(
        db: AsyncSession,
        query_params: dict
):
    list_stmt = (select(Posts).options(
        selectinload(Posts.house),
        selectinload(Posts.replies),
        selectinload(Posts.user)))
    total_stmt = select(func.count(Posts.post_id))
    return await common_query_list(db, query_params, total_stmt, list_stmt, Posts)


# 查询详情
async def get_post_by_id(
        db: AsyncSession,
        post_id: int
):
    stmt = (select(Posts).options(
        selectinload(Posts.house),
        selectinload(Posts.replies),
        selectinload(Posts.user),
    )
            .where(Posts.post_id == post_id))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# 新增
async def add_post(
        db: AsyncSession,
        post: dict,
):
    new_posts = Posts(**post)
    db.add(new_posts)
    await db.commit()
    await db.refresh(new_posts)
    return new_posts


# 更新
async def update_post(
        db: AsyncSession,
        post: dict,
):
    post = await get_post_by_id(db, post.get('post_id'))
    if not post:
        return False
    update_stmt = update(Posts).where(Posts.post_id == post.post_id).values(**post)
    await db.execute(update_stmt)
    await db.commit()
    await db.refresh(post)
    return post


# 删除
async def delete_post(
        db: AsyncSession,
        post_id: int,
):
    post = await get_post_by_id(db, post_id)
    if not post:
        return False
    stmt = delete(Posts).where(Posts.post_id == post_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0
