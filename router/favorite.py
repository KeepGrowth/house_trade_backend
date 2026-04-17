import os

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Path, Body

import utils.auth
from config.mysql_config import *
from crud.favorite import get_my_favorites, delete_favorite, add_favorite, get_favorite_by_id, get_by_user_house_id, \
    delete_by_user_house_id
from schemas.favorite import FavoriteResponse, FavoriteListResponse
from utils.response import *

# 导入你已有的模型、CRUD、Pydantic

# 创建路由
router = APIRouter(
    prefix="/favorite",
    tags=["收藏模块"],
    responses={404: {"description": "未找到"}},
)


@router.get("/", summary="获取收藏列表", status_code=status.HTTP_200_OK)
async def get_favorite_houses_api(
        current_user: int = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """获取收藏列表"""
    total, favorites = await get_my_favorites(db, current_user)
    houses_list = [FavoriteResponse().model_validate(favorite) for favorite in favorites]
    res_data = FavoriteListResponse(favorites=houses_list, total=total)
    return success_response(message="获取成功", data=res_data)


# 删除收藏记录
@router.delete("/{favoriteId}/", summary="删除收藏记录", status_code=status.HTTP_200_OK)
async def delete_favorite_api(
        favoriteId: int = Path(..., title="收藏ID"),
        current_user: int = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """删除收藏记录"""
    # 删除收藏记录
    delete_result = await delete_favorite(db, favoriteId, current_user)
    if delete_result:
        return success_response(message="删除成功")
    else:
        return error_response(message="删除失败")


# 添加收藏记录
@router.post("/", summary="添加收藏记录", status_code=status.HTTP_200_OK)
async def add_favorite_api(
        house_id: int = Body(..., title="房屋ID", alias="houseId"),
        current_user: int = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """
    添加收藏或取消收藏
    :param house_id:
    :param current_user:
    :param db:
    :return:
    """
    # 查找是否存在此收藏
    record = await get_by_user_house_id(db, user_id=current_user, house_id=house_id)
    # 如果存在，则删除此收藏记录
    if record:
        # 删除收藏记录
        res = await delete_by_user_house_id(db, user_id=current_user, house_id=house_id)
        return success_response(message="删除成功")
    favorite_result = await add_favorite(db, house_id, current_user)
    if favorite_result:
        return success_response(message="添加成功")
    else:
        return error_response(message="添加失败")
