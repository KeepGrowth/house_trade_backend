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


# 上传用户头像
@router.post("/avatar", summary="上传用户头像", status_code=status.HTTP_200_OK)
async def upload_avatar_api(
        file: UploadFile = File(...),
        current_user: User = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """上传用户头像"""
    # 获取文件名
    filename = file.filename
    # 获取文件内容
    file_content = await file.read()
    # 保存文件
    file_path = os.path.join()
    if await save_file(file_path, file_content):
        # 保存成功
        # 更新用户头像
        await update_user_avatar(db, current_user.user_id, filename)
        return success_response(message="上传成功")
    else:
        # 保存失败
        return error_response(message="上传失败")


# 获取我的收藏列表
@router.get("/my-favorites", summary="获取我的收藏列表", status_code=status.HTTP_200_OK)
async def get_my_favorites_api(
        current_user: User = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """获取我的收藏列表"""
    favorites = await get_user_favorites(db, current_user.user_id)
    res_data = [HouseFavoriteResponse().model_validate(favorite) for favorite in favorites]
    return success_response(message="获取成功", data=res_data)


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
