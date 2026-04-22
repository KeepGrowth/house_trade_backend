import os

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query

import utils.auth
from config.mysql_config import *
from crud.favorite import get_by_user_house_id
from crud.house_images import create_house_image
from crud.houses import *
from crud.reviews import create_house_review, get_house_reviews
from crud.users import get_user_by_id
from models.base import User
from schemas.house import *
from schemas.reviews import ReviewCreate, ReviewResponse
from schemas.users import SafeUserResponse
from utils.response import *
from utils.itemCF import get_recommend_houses_list
from crud.orders import *

# 导入你已有的模型、CRUD、Pydantic

# 创建路由
router = APIRouter(
    prefix="/houses",
    tags=["房源模块"],
    responses={404: {"description": "未找到"}},
)


# 买房接口
@router.post("/buy", summary="买房接口", status_code=status.HTTP_200_OK)
async def buy_house_api(
        house_id: int = Body(..., title="房源ID", alias="houseId"),
        current_user_id: int = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """
    买房接口，购买成功后状态改为已售，
    :param house_id:
    :param current_user_id:
    :param db:
    :return:
    """
    house = await get_house_by_id(db, house_id)
    if house.sale_status != 1:
        return error_response(message="此房源已售出或下架")
    result = await update_house_sale_status(db, house_id, 2)
    order_dict = {
        "seller_id": house.user_id,
        "buyer_id": current_user_id,
        "amount": house.price
    }
    order = await add_orders(db, order_dict)
    if result and order:
        return success_response(message="购买成功")
    return error_response(message="购买失败")


# 获取房源列表
@router.get("/", summary="获取房源列表", status_code=status.HTTP_200_OK)
async def get_houses_api(
        db: AsyncSession = Depends(get_database)
):
    """获取房源列表"""
    houses = await get_houses(db)
    houses_list = [HouseResponse().model_validate(house) for house in houses]
    res_data = HouseListResponse(houses=houses_list, total=len(houses))
    return success_response(message="获取成功", data=res_data)


# 获取推荐房源
@router.get("/recommend", summary="获取推荐房源", status_code=status.HTTP_200_OK)
async def get_recommend_houses_api(
        db: AsyncSession = Depends(get_database),
        params: HouseQueryParams = Query(...)
):
    """获取推荐房源"""
    if params is None:
        params = {}
    total, houses = await query_houses(db, params.model_dump(exclude_unset=True, exclude_none=True))
    houses_list = [HouseResponse().model_validate(house) for house in houses]
    res_data = HouseListResponse(houses=houses_list, total=total)
    return success_response(message="获取成功", data=res_data)


# 条件查询房源
@router.post("/query", summary="条件查询房源", status_code=status.HTTP_200_OK)
async def get_recommend_houses_api(
        db: AsyncSession = Depends(get_database),
        params: dict = Body(None, title="查询参数")
):
    """条件查询房源"""
    if params is None:
        params = {}
    print(params)
    total, houses = await get_houses(db, params=params)
    houses_list = [HouseResponse().model_validate(house) for house in houses]
    res_data = HouseListResponse(houses=houses_list, total=total)
    return success_response(message="获取成功", data=res_data)


# 获取房源详情
@router.get("/{house_id}", summary="获取房源详情", status_code=status.HTTP_200_OK)
async def get_house_api(
        house_id: int,
        db: AsyncSession = Depends(get_database),
        current_user_id: int = Depends(utils.auth.get_current_user),
):
    """获取房源详情"""
    house = await get_house_by_id(db, house_id)
    if not house:
        raise HTTPException(status_code=400, detail="房源不存在")

    # 售卖者信息
    seller_info = await get_user_by_id(db, house.user_id)
    seller_info = SafeUserResponse().model_validate(seller_info)

    # 评价信息
    review_list = await get_house_reviews(db, house_id)
    review_list = [ReviewResponse().model_validate(review) for review in review_list]

    # 是否被此用户收藏
    result = await get_by_user_house_id(db, current_user_id, house_id)
    is_favorite = 1 if result else 0

    res_data = HouseResponse().model_validate(house)
    res_data.seller_info = seller_info
    res_data.review_info = review_list
    res_data.is_favorite = is_favorite
    return success_response(message="获取成功", data=res_data)


# 发布新房源
@router.post("/", summary="发布新房源", status_code=status.HTTP_200_OK)
async def create_house_api(
        house: HouseCreate,
        current_user: int = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """发布新房源"""
    new_house = await create_house(db, house.model_dump(exclude_unset=True, exclude_none=True, exclude={'image_urls'}),
                                   current_user)

    # 将图片路径加到数据库中
    for image_url in house.image_urls:
        await create_house_image(db, house_id=new_house.house_id, image_url=image_url)
    res_data = HouseResponse().model_validate(new_house)
    return success_response(message="发布成功", data=res_data)


# # 编辑房源信息
# @router.put("/{house_id}", summary="编辑房源信息", status_code=status.HTTP_200_OK)
# async def update_house_api(
#         house_id: int,
#         house: HouseUpdate,
#         current_user: User = Depends(utils.auth.get_current_user),
#         db: AsyncSession = Depends(get_database)
# ):
#     """编辑房源信息"""
#     house = await get_house_by_id(db, house_id)
#     if not house:
#         raise HTTPException(status_code=400, detail="房源不存在")
#     updated_house = await update_house(db, house_id, house)
#     res_data = HouseResponse().model_validate(updated_house)


# 下架/删除房源
@router.delete("/{house_id}", summary="下架/删除房源", status_code=status.HTTP_200_OK)
async def delete_house_api(
        house_id: int,
        current_user: User = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """下架/删除房源"""
    house = await get_house_by_id(db, house_id)
    if not house:
        raise HTTPException(status_code=400, detail="房源不存在")
    await delete_house(db, house_id)
    return success_response(message="删除成功")


# 查询房源审核状态
@router.get("/{house_id}/audit-status", summary="查询房源审核状态", status_code=status.HTTP_200_OK)
async def get_house_audit_status_api(
        house_id: int,
        current_user: User = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """查询房源审核状态"""
    house = await get_house_by_id(db, house_id)
    if not house:
        raise HTTPException(status_code=400, detail="房源不存在")
    res_data = HouseAuditStatusResponse().model_validate(house)
    return success_response(message="查询成功", data=res_data)


# 收藏/取消收藏房源
# @router.post("/{house_id}/favorite", summary="收藏/取消收藏房源", status_code=status.HTTP_200_OK)
# async def favorite_house_api(
#         house_id: int,
#         current_user: User = Depends(utils.auth.get_current_user),
#         db: AsyncSession = Depends(get_database)
# ):
#     """收藏/取消收藏房源"""
#     house = await get_house_by_id(db, house_id)
#     if not house:
#         raise HTTPException(status_code=400, detail="房源不存在")
#     await favorite_house(db, house_id, current_user.user_id)
#     return success_response(message="操作成功")


# 提交房源评价（评分+内容）
@router.post("/{house_id}/reviews", summary="提交房源评价（评分+内容）", status_code=status.HTTP_200_OK)
async def create_house_review_api(
        house_id: int,
        review: ReviewCreate,
        current_user: int = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """提交房源评价（评分+内容）"""
    house = await get_house_by_id(db, house_id)
    if not house:
        raise HTTPException(status_code=400, detail="房源不存在")
    new_review = await create_house_review(db, house_id, review.model_dump(), current_user)
    res_data = ReviewResponse().model_validate(new_review)
    return success_response(message="评价成功", data=res_data)
