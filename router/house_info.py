from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from config.mysql_config import get_database
# 导入CRUD、模型、数据库依赖
from crud.house_info import *
from utils.auth import get_current_user

router = APIRouter(
    prefix="/houses",
    tags=["房源管理"],
    responses={404: {"description": "房源不存在"}},
    # 全局鉴权，非登录不可获取。
    dependencies=[Depends(get_current_user)]
)


# 创建房源
@router.post("/", summary="创建房源", status_code=status.HTTP_201_CREATED)
async def create_house_api(
        house: HouseCreate,
        db: AsyncSession = Depends(get_database)
):
    return await create_house(db, house)


# 获取所有房源（分页）
@router.get("/", summary="获取房源列表")
async def get_houses_api(
        skip: int = 0,
        limit: int = 10,
        db: AsyncSession = Depends(get_database)
):
    return await get_houses(db, skip=skip, limit=limit)


# 获取单个房源详情
@router.get("/{house_id}", summary="获取房源详情")
async def get_house_api(
        house_id: int,
        db: AsyncSession = Depends(get_database)
):
    house = await get_house_by_id(db, house_id)
    if not house:
        raise HTTPException(status_code=404, detail="房源不存在")
    return house


# 获取某个用户的房源
@router.get("/user/{user_id}", summary="获取用户发布的房源")
async def get_user_houses_api(
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        db: AsyncSession = Depends(get_database)
):
    return await get_houses_by_user_id(db, user_id, skip, limit)


# 条件筛选房源（区域/小区）
@router.get("/filter/list", summary="筛选房源")
async def filter_houses_api(
        district: Optional[str] = None,
        community: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
        db: AsyncSession = Depends(get_database)):
    return await get_houses_by_district_community(db, district, community, skip, limit)


# 更新房源
@router.put("/{house_id}", summary="更新房源信息")
async def update_house_api(
        house_id: int,
        house_update: HouseUpdate,
        db: AsyncSession = Depends(get_database)
):
    house = await update_house(db, house_id, house_update)
    if not house:
        raise HTTPException(status_code=404, detail="房源不存在")
    return house


# 删除房源
@router.delete("/{house_id}", summary="删除房源", status_code=status.HTTP_204_NO_CONTENT)
async def delete_house_api(
        house_id: int,
        db: AsyncSession = Depends(get_database)
):
    success = await delete_house(db, house_id)
    if not success:
        raise HTTPException(status_code=404, detail="房源不存在")
    return
