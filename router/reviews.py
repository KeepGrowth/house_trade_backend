import os

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Body, Path

import utils.auth
from config.mysql_config import *
from crud.reviews import get_reviews, get_review_by_id, delete_review, update_review
from crud.users import *
from schemas.reviews import ReviewResponse, ReviewListResponse
from schemas.users import *
from utils.response import *

# 导入你已有的模型、CRUD、Pydantic

# 创建路由
router = APIRouter(
    prefix="/reviews",
    tags=["评价模块"],
    responses={404: {"description": "未找到"}},
)


# 删除评价
@router.delete("/{review_id}", summary="删除自己的评价", status_code=status.HTTP_200_OK)
async def delete_review_api(
        review_id: int = Path(..., title="评价ID"),
        current_user: User = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """删除评价"""
    review = await get_review_by_id(db, review_id)
    if not review:
        raise HTTPException(status_code=400, detail="评价不存在")
    await delete_review(db, review_id)
    return success_response(message="删除成功")


# 条件分页查询评价列表
@router.post("/query", summary="条件分页查询评价列表", status_code=status.HTTP_200_OK)
async def get_reviews_api(
        params: dict = Body(None, title="查询参数"),
        current_user: User = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """条件分页查询评价列表"""
    if params is None:
        params = {}
    print(params)
    total, reviews = await get_reviews(db, params=params)
    reviews_list = [ReviewResponse().model_validate(review) for review in reviews]
    res_data = ReviewListResponse(reviews=reviews_list, total=total)
    return success_response(message="获取成功", data=res_data)


# 切换显示隐藏状态x`
@router.post("/switch_status", summary="切换显示隐藏状态", status_code=status.HTTP_200_OK)
async def switch_status_api(
        review_id: int = Body(..., title="评价ID", alias="reviewId"),
        current_user: User = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """切换显示隐藏状态"""
    review = await get_review_by_id(db, review_id)
    if not review:
        raise HTTPException(status_code=400, detail="评价不存在")
    review.status = 1 if review.status == 0 else 0
    await db.commit()
    await db.refresh(review)
    return success_response(message="切换成功", data=ReviewResponse().model_validate(review))
