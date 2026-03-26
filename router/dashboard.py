import os

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File

import utils.auth
from config.mysql_config import *
from crud.house_images import create_house_image
from crud.houses import *
from crud.reviews import create_house_review, get_house_reviews
from crud.users import get_user_by_id, get_all_users
from models.base import User
from schemas.house import *
from schemas.reviews import ReviewCreate, ReviewResponse
from schemas.users import SafeUserResponse
from utils.response import *

# 导入你已有的模型、CRUD、Pydantic

# 创建路由
router = APIRouter(
    prefix="/dashboard",
    tags=["数据看板模块"],
    responses={404: {"description": "未找到"}},
)


@router.get("/indicator", summary="数据指标看板", status_code=status.HTTP_200_OK)
async def dashboard_api(
        current_user: int = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """
    数据指标看板
    :param current_user:
    :param db:
    :return:
    """
    # 总用户数
    total_users = await get_all_users(db)
    total_users = len(total_users)
    # 总房源数
    total_houses = await get_all_houses(db)
    total_houses = len(total_houses)
    # 待审核房源
    total_houses_audit = await get_houses(db, params={"audit_status": 0, "page_size": total_houses})
    total_houses_audit = len(total_houses_audit)

    return success_response(message="获取成功", data={
        "total_users": total_users,
        "total_houses": total_houses,
        "total_houses_audit": total_houses_audit
    })


# 获取注册用户数趋势
@router.get("/users", summary="获取注册用户数趋势", status_code=status.HTTP_200_OK)
async def get_users_api(
        current_user: int = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """
    获取注册用户数趋势
    :param current_user:
    :param db:
    :return:
    """
    users = await get_all_users(db)
    # 获取最近一周用户的注册趋势
    user_list = [SafeUserResponse().model_validate(user) for user in users]
    user_frame = pd.DataFrame(user_list)
    user_frame['create_time'] = pd.to_datetime(user_frame['create_time'])
    user_frame.set_index('create_time', inplace=True)
    user_frame = user_frame.resample('D').count()
    print(user_frame)
    x_axis = user_frame.index.tolist()
    y_axis = user_frame['id'].tolist()
    return success_response(message="获取成功", data=user_frame.to_dict())
