import os
import random
from datetime import timedelta

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query

import utils.auth
from config.mysql_config import *
from crud import orders
from crud.house_images import create_house_image
from crud.houses import *
from crud.reviews import create_house_review, get_house_reviews
from crud.users import get_user_by_id, get_all_users
from models.base import User
from schemas.dashboard import QueryParams
from schemas.house import *
from schemas.reviews import ReviewCreate, ReviewResponse
from schemas.users import SafeUserResponse, UsersQueryParams
from utils.ai_analyse import chat_with_ollama, chat_with_ollama1
from utils.response import *
from crud.users import *
from crud.orders import *

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
    # 累计成交额
    order_result = await orders.get_all_orders(db)
    order_list = [r.__dict__ for r in order_result]
    order_df = pd.DataFrame(order_list)
    if len(order_df) == 0:
        return success_response(message="获取成功", data={
            "total_users": total_users,
            "total_houses": total_houses,
            "total_houses_audit": total_houses_audit,
            "total_orders_amount": 0,
            "total_orders_count": 0,
        })
    total_orders_amount = order_df['amount'].sum()
    total_orders_count = len(order_result)
    return success_response(message="获取成功", data={
        "total_users": total_users,
        "total_houses": total_houses,
        "total_houses_audit": total_houses_audit,
        "total_orders_amount": total_orders_amount,
        "total_orders_count": total_orders_count,
    })


# 获取注册用户数趋势
@router.get("/users", summary="获取注册用户数趋势", status_code=status.HTTP_200_OK)
async def get_users_api(
        query_params: UsersQueryParams = Query(...),
        current_user: int = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """
    条件查询-获取注册用户数趋势
    """
    total, users = await query_users(db, query_params.model_dump(exclude_none=True, exclude_unset=True))
    user_list = [user.__dict__ for user in users]
    user_frame = pd.DataFrame(user_list)
    user_frame['create_time'] = pd.to_datetime(user_frame['create_time'])
    # 获取用户周期的注册趋势数据
    user_frame.set_index('create_time', inplace=True)
    user_frame = user_frame.resample('W').count()
    # 日期转成字符串
    user_frame.reset_index(inplace=True)
    user_frame['create_time'] = user_frame['create_time'].dt.strftime('%Y-%m-%d')
    user_frame.set_index('create_time', inplace=True)
    x_axis = user_frame.index.tolist()
    y_axis = user_frame['user_id'].tolist()
    return success_response(message="获取成功", data={
        "x_axis": x_axis,
        "y_axis": y_axis,
    })


# 1. 定义一个随机颜色生成函数 (生成 Hex 颜色)
def get_random_color():
    # 生成 #RRGGBB 格式的随机颜色
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))


# 房源区域分布
@router.get("/house-areas", summary="获取房源区域分布", status_code=status.HTTP_200_OK)
async def get_house_areas_api(
        query_params: QueryParams = Query(...),
        current_user: int = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """
    获取房源区域分布饼图数据
    """
    total, houses = await query_houses(db, query_params.model_dump(exclude_none=True, exclude_unset=True))
    house_list = [house.__dict__ for house in houses]
    house_frame = pd.DataFrame(house_list)
    if len(house_frame) == 0:
        return success_response(message="获取成功", data=[])
    house_frame['district'] = house_frame['district'].fillna('未知')
    house_frame = house_frame.groupby('district').size().reset_index(name='value')
    house_frame = house_frame.rename(columns={'district': 'name'})
    data_list = [
        {
            "name": row['name'],
            "value": row['value'],
            "itemStyle": {
                "color": get_random_color(),  # 随机颜色
                "borderRadius": 4  # 固定圆角
            }
        }
        for _, row in house_frame.iterrows()
    ]
    return success_response(message="获取成功", data=data_list)


# 房源新增情况
@router.get("/house-add", summary="获取房源新增情况", status_code=status.HTTP_200_OK)
async def get_house_add_api(
        query_params: QueryParams = Query(...),
        current_user: int = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """

    :param query_params:
    :param current_user:
    :param db:
    :return:
    """
    total, houses = await query_houses(db, query_params.model_dump(exclude_none=True, exclude_unset=True))
    house_list = [house.__dict__ for house in houses]
    house_frame = pd.DataFrame(house_list)
    if len(house_frame) == 0:
        return success_response(message="获取成功", data=[])
    house_frame['create_time'] = pd.to_datetime(house_frame['create_time'])
    # 获取用户周期的注册趋势数据
    house_frame.set_index('create_time', inplace=True)
    house_frame = house_frame.resample('D').count()
    # 日期转成字符串
    house_frame.reset_index(inplace=True)
    house_frame['create_time'] = house_frame['create_time'].dt.strftime('%Y-%m-%d')
    house_frame.set_index('create_time', inplace=True)
    x_axis = house_frame.index.tolist()
    y_axis = house_frame['house_id'].tolist()
    return success_response(message="获取成功", data={
        "x_axis": x_axis,
        "y_axis": y_axis,
    })


# 成交额趋势
@router.get("/orders-sale", summary="获取成交额趋势", status_code=status.HTTP_200_OK)
async def get_orders_sale_api(
        query_params: QueryParams = Query(...),
        current_user: int = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """
    获取成交额趋势柱状图数据
    :param query_params:
    :param current_user:
    :param db:
    :return:
    """
    total, orders_result = await query_orders(db, query_params.model_dump(exclude_none=True, exclude_unset=True))
    orders_list = [order.__dict__ for order in orders_result]
    order_frame = pd.DataFrame(orders_list)
    if len(order_frame) == 0:
        return success_response(message="获取成功", data=[])
    order_frame['create_time'] = pd.to_datetime(order_frame['create_time'])
    order_frame.set_index('create_time', inplace=True)
    order_frame = order_frame.resample('D')
    daily_amounts = order_frame['amount'].resample('D').sum()
    categories = daily_amounts.index.strftime('%Y-%m-%d').tolist()  # 顺便格式化日期为字符串
    data = daily_amounts.tolist()
    return success_response(message="获取成功", data={
        "categories": categories,
        "data": data,
    })


# 获取AI统计信息
@router.get("/ai-stats", summary="获取AI总结的统计信息")
async def get_ai_stats(
        current_user: int = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """
    获取AI总结的统计信息
    :param current_user:
    :param db:
    :return:
    """
    # 获取用户总数、近一周新增用户数
    total_users = await get_all_users(db)
    user_models = [SafeUserResponse.model_validate(user) for user in total_users]
    user_dicts = [model.model_dump() for model in user_models]
    user_frame = pd.DataFrame(user_dicts)
    # 统计用户总数
    total_users = len(user_frame)
    print(user_frame)
    # 统计近一周新增用户数
    total_new_users = user_frame[user_frame['create_time'] > (datetime.now() - timedelta(days=7))]['user_id'].count()

    # 在售房源数、近一周审核通过的房源数
    total, total_houses = await get_houses(db, params={"audit_status": 1})
    house_model = [HouseResponse.model_validate(house) for house in total_houses]
    house_dicts = [model.model_dump() for model in house_model]
    house_frame = pd.DataFrame(house_dicts)
    total_houses = len(house_frame)

    # 让AI生成响应对话
    prompt = f"""
    用户总数：{total_users},
    近一周新增用户数：{total_new_users},
    在售房源数：{total_houses},
    近一周审核通过的房源数：{total_houses},
    """
    result = await chat_with_ollama1("deepseek-r1:1.5b", prompt)
    print(result)
    return success_response(message="获取成功", data={
        'text': result,
    })
