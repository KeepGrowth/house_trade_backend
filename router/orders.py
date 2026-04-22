from fastapi import APIRouter, Depends, HTTPException, status, Query, Path

import utils.auth
from config.mysql_config import *
from crud.orders import *
from schemas.orders import *
from utils.response import *

# 创建路由
router = APIRouter(
    prefix="/orders",
    tags=["帖子模块"],
    responses={404: {"description": "未找到"}},
)


@router.get('/list')
async def get_orders_api(
        query_params: OrderQueryParams = Query(...),
        current_user_id: int = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """
    条件查询帖子列表
    """
    total, orders_result = await query_orders(db, query_params.model_dump(exclude_unset=True, exclude_none=True))
    orders_list = [OrderItemResponse().model_validate(order) for order in orders_result]
    res_data = OrderListResponse(orders=orders_list, total=total)
    return success_response(message="获取成功", data=res_data)


@router.get('/detail/{order_id}')
async def get_order_detail_api(
        order_id: int,
        db: AsyncSession = Depends(get_database),
        current_user_id: int = Depends(utils.auth.get_current_user),
):
    """
    获取帖子详情
    """
    order = await get_order_by_id(db, order_id)
    if not order:
        return error_response(message="帖子不存在")
    order = OrderItemResponse().model_validate(order)
    return success_response(message="获取成功", data=order)


@router.post('/add')
async def add_order_api(
        order_data: OrderAddRequest,
        db: AsyncSession = Depends(get_database),
        current_user_id: int = Depends(utils.auth.get_current_user),
):
    """
    添加帖子
    """
    try:
        order_data.user_id = current_user_id
        order = await add_orders(db, order_data.model_dump(exclude_unset=True, exclude_none=True))
        if not order:
            return error_response(message="添加失败")
        order = OrderItemResponse().model_validate(order)
        return success_response(message="添加成功", data=order)
    except Exception as e:
        return error_response(message='添加房源不存在' + str(e))


@router.put('/update')
async def update_order_api(
        order_data: OrderUpdateRequest,
        db: AsyncSession = Depends(get_database),
        current_user_id: int = Depends(utils.auth.get_current_user),
):
    """
    更新帖子
    """
    order_data.user_id = current_user_id
    result = await update_orders(db, order_data.model_dump(exclude_unset=True, exclude_none=True))
    if not result:
        return error_response(message="更新失败")
    return success_response(message="更新成功")


@router.delete('/delete/{order_id}')
async def delete_order_api(
        order_id: int = Path(...),
        db: AsyncSession = Depends(get_database),
        current_user_id: int = Depends(utils.auth.get_current_user),
):
    """
    删除帖子
    """
    order = await get_order_by_id(db, order_id)
    if not order:
        return error_response(message="帖子不存在")
    if order.user_id != current_user_id:
        return error_response(message="无权限删除")
    result = await del_order(db, order_id)
    if not result:
        return error_response(message="删除失败")
    return success_response(message="删除成功")
