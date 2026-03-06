from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from config.mysql_config import get_database
from crud.user_review import *
from utils.auth import get_current_user

router = APIRouter(
    prefix="/reviews",
    tags=["房源评价管理"],
    dependencies=[Depends(get_current_user)]

)


# 发布评价
@router.post("/", summary="发布评价", status_code=status.HTTP_201_CREATED)
async def add_review(
        review: ReviewCreate,
        db: AsyncSession = Depends(get_database)
):
    return await create_review(db, review)


# 获取单个评价
@router.get("/{review_id}", summary="获取评价详情")
async def get_review(
        review_id: int,
        db: AsyncSession = Depends(get_database)
):
    rev = await get_review_by_id(db, review_id)
    if not rev:
        raise HTTPException(status_code=404, detail="评价不存在")
    return rev


# 获取房源的所有评价
@router.get("/house/{house_id}", summary="获取房源评价列表")
async def list_house_reviews(
        house_id: int,
        skip: int = 0,
        limit: int = 10,
        db: AsyncSession = Depends(get_database)
):
    return await get_reviews_by_house(db, house_id, skip, limit)


# 获取用户的所有评价
@router.get("/user/{user_id}", summary="获取用户发表的评价")
async def list_user_reviews(
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        db: AsyncSession = Depends(get_database)
):
    return await get_reviews_by_user(db, user_id, skip, limit)


# 修改评价
@router.put("/{review_id}", summary="修改评价")
async def modify_review(
        review_id: int,
        review_update: ReviewUpdate,
        db: AsyncSession = Depends(get_database)
):
    rev = await update_review(db, review_id, review_update)
    if not rev:
        raise HTTPException(status_code=404, detail="评价不存在")
    return rev


# 删除/隐藏评价
@router.delete("/{review_id}", summary="删除评价", status_code=status.HTTP_204_NO_CONTENT)
async def remove_review(
        review_id: int,
        db: AsyncSession = Depends(get_database)
):
    if not await delete_review(db, review_id):
        raise HTTPException(status_code=404, detail="评价不存在")
