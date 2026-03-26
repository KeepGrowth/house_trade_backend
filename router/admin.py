import os

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Body, Path

import utils.auth
from config.mysql_config import *
from crud.houses import get_houses, get_house_by_id, update_house_audit_status
from crud.users import *
from models.base import User
from schemas.admin import UserQueryParams, AuditParams
from schemas.house import HouseResponse, HouseListResponse
from schemas.users import *
from utils.response import *

# 导入你已有的模型、CRUD、Pydantic

# 创建路由
router = APIRouter(
    prefix="/admin",
    tags=["管理员模块"],
    responses={404: {"description": "未找到"}},
)


# 获取核心统计概览数据
@router.get("/stats/overview", summary="获取核心统计概览数据", status_code=status.HTTP_200_OK)
async def get_statistics_api(
        current_user: User = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """获取核心统计概览数据"""
    statistics = await get_statistics(db)
    res_data = StatisticsResponse().model_validate(statistics)
    return success_response(message="获取成功", data=res_data)


# 获取趋势数据
@router.get("/stats/trends", summary="获取趋势数据", status_code=status.HTTP_200_OK)
async def get_trends_api(
        current_user: User = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """获取趋势数据"""
    trends = await get_trends(db)
    res_data = TrendsResponse(trends=trends)
    return success_response(message="获取成功", data=res_data)


# 获取区域分布数据
@router.get("/stats/district-dist", summary="获取区域分布数据", status_code=status.HTTP_200_OK)
async def get_districts_api(
        current_user: User = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """ 获取区域分布数据"""
    districts = await get_districts(db)
    res_data = [DistrictResponse().model_validate(district) for district in districts]
    return success_response(message="获取成功", data=res_data)


# 获取待审核房源列表
@router.post("/audit/list", summary="获取待审核房源列表", status_code=status.HTTP_200_OK)
async def get_pending_houses_api(
        params: AuditParams = Body(None, alias="queryParams"),
        current_user: User = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """获取待审核房源列表"""
    page = params.page
    page_size = params.page_size
    print(params)
    total, houses = await get_houses(db, page, page_size,
                                     params=params.model_dump(exclude={"page", "page_size"}, exclude_unset=True,
                                                              exclude_none=True))
    houses_list = [HouseResponse().model_validate(house) for house in houses]
    res_data = HouseListResponse(houses=houses_list, total=total)
    return success_response(message="获取成功", data=res_data)


# 提交审核结果
@router.post("/audit/verify", summary="提交审核结果", status_code=status.HTTP_200_OK)
async def verify_house_api(
        house_id: int = Body(None, title="房源ID", alias="houseId"),
        status: int = Body(None, title="审核状态", alias="auditStatus"),
        current_user: User = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """提交审核结果"""
    house = await get_house_by_id(db, house_id)
    if not house:
        return error_response(message="房源不存在")
    await update_house_audit_status(db, house_id, status)
    return success_response(message="审核成功")


# 获取用户列表
@router.post("/users", summary="获取用户列表", status_code=status.HTTP_200_OK)
async def get_users_api(
        current_user: User = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database),
        params: UserQueryParams = Body(None, alias="queryParams")
):
    """获取用户列表"""
    page = params.page
    page_size = params.page_size
    role = params.role
    username = params.username
    print("params:", params)
    total, users = await get_users(db, page, page_size, role, username)
    user_list = [SafeUserResponse().model_validate(user) for user in users]
    res_data = UserListResponse(users=user_list, total=total)
    return success_response(message="获取成功", data=res_data)


# 冻结/解封用户
@router.post("/users/freeze", summary="冻结/解封用户", status_code=status.HTTP_200_OK)
async def freeze_user_api(
        user_id: int,
        status: int,
        current_user: User = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """冻结/解封用户"""
    user = await get_user_by_id(db, user_id)
    if not user:
        return error_response(message="用户不存在")
    await freeze_user(db, user_id, status)
    return success_response(message="操作成功")


# 获取全站评价列表
@router.get("/reviews", summary="获取全站评价列表", status_code=status.HTTP_200_OK)
async def get_reviews_api(
        current_user: User = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """获取全站评价列表"""
    reviews = await get_reviews(db)
    reviews_list = [ReviewResponse().model_validate(review) for review in reviews]
    res_data = ReviewListResponse(reviews=reviews_list, total=len(reviews))
    return success_response(message="获取成功", data=res_data)


# 隐藏/显示违规评论
@router.post("/reviews/{review_id}/hide", summary="隐藏/显示违规评论", status_code=status.HTTP_200_OK)
async def hide_review_api(
        review_id: int,
        status: int,
        current_user: User = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """隐藏/显示违规评论"""
    review = await get_review_by_id(db, review_id)
    if not review:
        return error_response(message="评价不存在")
    await hide_review(db, review_id, status)
    return success_response(message="操作成功")


# 删除用户
@router.delete("/users/{user_id}", summary="删除用户", status_code=status.HTTP_200_OK)
async def delete_user_api(
        user_id: int = Path(..., title="用户ID"),
        current_user: User = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """删除用户"""
    user = await get_user_by_id(db, user_id)
    if not user:
        return error_response(message="用户不存在")
    await delete_user(db, user_id)
    return success_response(message="删除成功")
