from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from config.mysql_config import get_database
from crud.house_favorite import *

router = APIRouter(
    prefix="/favorites",
    tags=["房源收藏管理"],
)


# 1. 添加收藏
@router.post("/", summary="添加收藏", status_code=status.HTTP_201_CREATED)
async def add_favorite(
        fav: FavoriteCreate,
        db: AsyncSession = Depends(get_database)
):
    return await create_favorite(db, fav)


# 2. 查询用户是否收藏某房源
@router.get("/check", summary="检查是否已收藏")
async def check_favorite(
        user_id: int,
        house_id: int,
        db: AsyncSession = Depends(get_database)
):
    fav = await get_user_favorite(db, user_id, house_id)
    return {"is_favorited": fav is not None and fav.is_deleted == 0}


# 3. 获取用户收藏列表
@router.get("/user/{user_id}", summary="获取用户收藏列表")
async def list_user_favorites(
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        db: AsyncSession = Depends(get_database)
):
    return await get_user_favorites(db, user_id, skip, limit)


# 4. 取消收藏
@router.delete("/", summary="取消收藏")
async def remove_favorite(
        fav: FavoriteCreate,
        db: AsyncSession = Depends(get_database)
):
    ok = await cancel_favorite(db, fav.user_id, fav.house_id)
    if not ok:
        raise HTTPException(status_code=404, detail="收藏记录不存在")
    return {"message": "取消收藏成功"}


# 5. 获取房源收藏数
@router.get("/count/{house_id}", summary="获取房源收藏数")
async def count_favorites(
        house_id: int,
        db: AsyncSession = Depends(get_database)
):
    count = await get_favorite_count(db, house_id)
    return {"house_id": house_id, "favorite_count": count}
