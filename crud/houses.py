from typing import List, Optional

from fastapi import Body
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from crud.users import get_user_by_id
from models.base import House, Review


# 获取所有房源
async def get_all_houses(
        db: AsyncSession,
):
    houses = await db.execute(select(House))
    return houses.scalars().all()


# 条件查询获取房源列表
async def get_houses(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        params: Optional[dict] = None
):
    """
    条件查询获取房源列表
    修复点：
    1. 修复总数统计查询忽略过滤条件的问题。
    2. 修复总数统计查询的 SQL 构建语法错误。
    3. 增加默认排序，防止分页数据不稳定。
    4. 修复 audit_status 为 0 时无法查询的问题。
    5. 确保计数查询不包含 offset/limit/options。
    """
    # 基础参数校验
    page = max(page, 1)
    page_size = max(page_size, 1)

    if params is None:
        params = {}

    # 1. 构建基础查询结构 (不含分页和排序，用于后续复用过滤条件)
    # 注意：先不添加 options，因为计数查询不需要它，且避免污染
    base_query = select(House)

    # --- 应用过滤条件 (提取为一个内部逻辑块，避免重复代码) ---

    # 1. 精确匹配：house_id
    if params.get("house_id") is not None:
        base_query = base_query.where(House.house_id == params["house_id"])

    # 2. 包含查询优化：district
    district_val = params.get("district")
    if district_val:
        if isinstance(district_val, str):
            district_list = [d.strip() for d in district_val.split(',') if d.strip()]
        else:
            district_list = district_val

        if district_list:
            base_query = base_query.where(House.district.in_(district_list))

    # 3. 包含查询优化：house_type
    house_type_val = params.get("house_type")
    if house_type_val:
        if isinstance(house_type_val, str):
            house_type_list = [t.strip() for t in house_type_val.split(',') if t.strip()]
        else:
            house_type_list = house_type_val

        if house_type_list:
            base_query = base_query.where(House.house_type.in_(house_type_list))

    # 4. 价格范围查询
    min_price = params.get('min_price')
    max_price = params.get('max_price')

    if min_price is not None:
        base_query = base_query.where(House.price >= min_price)
    if max_price is not None:
        base_query = base_query.where(House.price <= max_price)

    # 5. 按审核状态查询 (修复 0 值被忽略的问题)
    if 'audit_status' in params and params['audit_status'] is not None:
        base_query = base_query.where(House.audit_status == params['audit_status'])
    # 6. 模糊匹配：title
    title_val = params.get("title")
    if title_val:
        base_query = base_query.where(House.title.like(f'%{title_val}%'))

    # --- 构建最终的分页查询 (带 Options, Limit, Offset, OrderBy) ---
    query = base_query.options(selectinload(House.images))

    # 排序逻辑
    order_by_field = params.get('order_by')
    sorted_applied = False

    if order_by_field:
        allowed_fields = {
            'price': House.price,
            'create_time': getattr(House, 'create_time', House.house_id),  # 兜底
            'updated_at': getattr(House, 'updated_at', House.house_id),
        }

        sort_dir = 'asc'
        field_name = order_by_field

        if order_by_field.startswith('-'):
            sort_dir = 'desc'
            field_name = order_by_field[1:]
        elif '_desc' in order_by_field:
            sort_dir = 'desc'
            field_name = order_by_field.replace('_desc', '')

        if field_name in allowed_fields:
            column = allowed_fields[field_name]
            if sort_dir == 'desc':
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())
            sorted_applied = True

    # 【重要】如果没有应用有效排序，必须添加默认排序 (通常是主键)，否则分页会乱
    if not sorted_applied:
        query = query.order_by(House.house_id.desc())

    # 应用分页
    query = query.offset((page - 1) * page_size).limit(page_size)

    # --- 构建总数统计查询 ---
    # 从 base_query 克隆，移除可能的默认排序（如果有），替换为 count
    # 注意：base_query 此时还没有加 options/limit/offset，非常适合做计数
    count_query = select(func.count()).select_from(base_query.subquery())
    # 或者更直接的方式 (取决于 SQLAlchemy 版本，2.0+ 推荐下面这种)
    # total_stmt = select(func.count()).select_from(House).where(*base_query._where_criteria)
    # 但最稳妥的方式是复用 base_query 的结构：

    # SQLAlchemy 2.0 标准写法：
    total_stmt = select(func.count()).select_from(base_query.subquery())

    # 执行查询
    # 并行执行或串行执行均可，这里串行以保证事务一致性逻辑清晰
    total_result = await db.execute(total_stmt)
    total = total_result.scalar_one()

    if total == 0:
        return 0, []

    result = await db.execute(query)
    houses = result.scalars().all()

    return total, houses


# 获取单个房源信息
async def get_house_by_id(
        db: AsyncSession,
        house_id: int
):
    """
    获取单个房源信息
    :param db:
    :param house_id:
    :return:
    """
    query = select(House).where(House.house_id == house_id)
    house = await db.execute(query)
    return house.scalars().first()


# 更改房源审核状态
async def update_house_audit_status(
        db: AsyncSession,
        house_id: int,
        audit_status: int
):
    """
    更改房源审核状态
    :param db:
    :param house_id:
    :param audit_status:
    :return:
    """
    house = await get_house_by_id(db, house_id)
    house.audit_status = audit_status
    await db.commit()
    return house


# 新增房源
async def create_house(
        db: AsyncSession,
        house: dict,
        user_id: int
):
    """
    新增房源
    :param db:
    :param house:
    :param user_id:
    :return:
    """
    house = House(
        **house,
        user_id=user_id
    )
    db.add(house)
    await db.commit()
    await db.refresh(house)
    return house


# 删除单个房源
async def delete_house(
        db: AsyncSession,
        house_id: Body(None, title="房源ID", alias="houseId")
):
    """
    删除单个房源
    :param db:
    :param house_id:
    :return:
    """
    house = await get_house_by_id(db, house_id)
    await db.delete(house)
    await db.commit()
    return house


# 获取某个用户的房源列表
async def get_user_houses(
        db: AsyncSession,
        user_id: int
):
    """
    获取某个用户的房源列表
    :param db:
    :param user_id:
    :return:
    """
    query = select(House).where(House.user_id == user_id)
    houses = await db.execute(query)
    return houses.scalars().all()
