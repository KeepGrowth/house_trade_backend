import os

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File

import utils.auth
from config.mysql_config import *
from crud.houses import get_user_houses
from crud.users import *
from schemas.house import HouseResponse, HouseListResponse
from schemas.users import *
from utils.response import *

# 导入你已有的模型、CRUD、Pydantic

# 创建路由
router = APIRouter(
    prefix="/users",
    tags=["用户模块"],
    responses={404: {"description": "未找到"}},
)


# 获取当前用户个人信息
@router.get("/profile", summary="获取当前用户个人信息", status_code=status.HTTP_200_OK)
async def get_profile_api(
        current_user: User = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """获取当前用户个人信息"""
    user = await get_user_by_id(db, current_user.user_id)
    if not user:
        raise HTTPException(status_code=400, detail="用户不存在")
    res_data = SafeUserResponse().model_validate(user)
    return success_response(message="获取成功", data=res_data)


# 修改个人资料
@router.put("/profile", summary="修改个人资料", status_code=status.HTTP_200_OK)
async def update_profile_api(
        user: UserUpdate,
        current_user: int = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """修改个人资料"""
    exist_user = await get_user_by_id(db, current_user)
    if not exist_user:
        raise HTTPException(status_code=400, detail="用户不存在")

    print(user)
    updated_user = await update_user(db, user.user_id, user)
    res_data = SafeUserResponse().model_validate(updated_user)
    return success_response(message="修改成功", data=res_data)




# 获取我发布的房源列表
@router.get("/my-houses", summary="获取我发布的房源列表", status_code=status.HTTP_200_OK)
async def get_my_houses_api(
        current_user: int = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """获取我发布的房源列表"""
    user = await get_user_by_id(db, current_user)
    if user.role != 2:
        raise HTTPException(status_code=400, detail="购房者无权限")
    houses = await get_user_houses(db, current_user)
    houses_list = [HouseResponse().model_validate(house) for house in houses]
    res_data = HouseListResponse(houses=houses_list, total=len(houses))
    return success_response(message="获取成功", data=res_data)
