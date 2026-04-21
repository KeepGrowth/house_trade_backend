from typing import Tuple, List, Type, Optional
from sqlalchemy import select, func, delete, inspect, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from fastapi import HTTPException
from starlette import status
import datetime
from pydantic import BaseModel


# 去除字典中的空值
def remove_empty_values(d: dict) -> dict:
    """
    移除字典中所有空值类型的键值对
    空值定义：None、''、[]、{}、()、0（可根据需求调整）
    """
    cleaned = {}
    for k, v in d.items():
        # 自定义过滤规则：判断值是否为“非空”
        if v not in (None, "", [], {}, ()):
            cleaned[k] = v
    return cleaned


# 通用分页查询方法
async def get_list_by_user_id(
        db: AsyncSession,
        model: Type[DeclarativeBase],  # 更语义化的参数名：model代替object_name
        user_id: int,
        page: int = 1,
        page_size: int = 10,
        extra_filter: Optional[any] = None,  # 扩展：支持额外过滤条件
):
    """
    通用分页查询方法：根据user_id查询指定模型的列表（带分页）
    Args:
        db: 异步数据库会话
        model: 要查询的ORM模型类（继承自DeclarativeBase）
        user_id: 筛选的用户ID
        page: 当前页码（默认1）
        page_size: 每页条数（默认10）
        extra_filter: 额外的过滤条件（可选，如：model.status == 1）

    Returns:
        Tuple[int, List]: 总条数、当前页数据列表
    """
    # 1. 校验分页参数（避免负数/0值导致SQL错误）
    page = max(page, 1)
    page_size = max(page_size, 1)
    page_size = min(page_size, 100)  # 限制最大页大小，防止一次性查太多数据

    # 2. 构建总条数查询语句（支持额外过滤）
    count_stmt = select(func.count(model.id)).where(model.user_id == user_id)
    if extra_filter is not None:
        count_stmt = count_stmt.where(extra_filter)

    # 3. 执行总条数查询（异常捕获+类型确保）
    try:
        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one() or 0  # 确保total是int，避免None
    except Exception as e:
        raise ValueError(f"查询{model.__name__}总条数失败: {str(e)}")

    # 4. 构建列表查询语句（分页+排序+额外过滤）
    offset = (page - 1) * page_size
    query_stmt = (
        select(model)
        .where(model.user_id == user_id)
        .order_by(model.create_time.desc())
        .offset(offset)
        .limit(page_size)
    )
    # 添加额外过滤条件
    if extra_filter is not None:
        query_stmt = query_stmt.where(extra_filter)

    # 5. 执行列表查询
    try:
        list_result = await db.execute(query_stmt)
        data_list = list_result.scalars().all()  # scalars()返回模型实例迭代器
    except Exception as e:
        raise ValueError(f"查询{model.__name__}列表失败: {str(e)}")
    return total, data_list


# 通用删除方法
async def delete_by_id(
        db: AsyncSession,
        model: Type[DeclarativeBase],
        id: int,
):
    """
    通用删除方法：根据id删除指定模型的数据
    Args:
        db: 异步数据库会话
        model: 要删除的ORM模型类（继承自DeclarativeBase）
        id: 要删除的记录ID
        user_id: 删除的用户ID
    Returns:
        int: 删除的行数
    """
    stmt = delete(model).where(model.id == id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount


# 通用查询方法
async def get_by_id(
        db: AsyncSession,
        model: Type[DeclarativeBase],
        item_id: int,
):
    stmt = select(model).where(model.id == item_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# 通用更新方法
async def update_by_id(
        db: AsyncSession,
        model: Type[DeclarativeBase],
        item_id: int,
        update_data: dict,
):
    item = await get_by_id(db, model, item_id)
    if not item:
        raise ValueError(f"{model.__name__}不存在")
    # 更新数据,忽略空值
    update_dict = remove_empty_values(update_data)
    for key, value in update_dict.items():
        if hasattr(item, key):
            setattr(item, key, value)
            item.update_time = datetime.datetime.now()
    item.update_time = datetime.datetime.now()
    await db.commit()
    await db.refresh(item)
    return item


# 通用新增方法
async def add(
        db: AsyncSession,
        model: Type[DeclarativeBase],
        user_id: int,
        add_data: dict,
        check_unique: bool = True,

):
    item = model(**add_data, user_id=user_id)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


# 通用条件分页查询方法
async def common_query_list(
        db: AsyncSession,
        query_params: dict,
        total_stmt,
        list_stmt,
        model: Type[DeclarativeBase],
):
    """
    分页条件查询模型数据列表
    :param db:
    :param query_params:
    :param model:SQLALCHEMY模型对象
    :return:
    """
    # 2. 定义允许的筛选字段白名单，防止非法字段注入
    mapper = inspect(model)
    allow_filter_keys = [key for key, value in mapper.columns.items()]
    print("允许查询的参数", allow_filter_keys)
    # 3. 提取并处理分页参数
    # 获取页码，默认为 1
    page = query_params.get('page', 1)
    try:
        page = int(page)
        page = max(1, page)  # 保证页码至少为 1
    except (ValueError, TypeError):
        page = 1

    # 获取每页数量，默认为 10
    page_size = query_params.get('page_size', 10)
    try:
        page_size = int(page_size)
        # 限制最大每页数量，防止恶意请求过大导致数据库压力
        page_size = min(page_size, 100)
    except (ValueError, TypeError):
        page_size = 10

    # 计算偏移量 (offset = (页码 - 1) * 每页数量)
    offset = (page - 1) * page_size

    # 提取筛选条件
    query_params.pop('page', None)
    query_params.pop('page_size', None)
    filter_conditions = []
    # 遍历筛选条件，只处理白名单内的字段
    for key in query_params.keys():
        value = query_params[key]

        model_field = getattr(model, key)
        filter_conditions.append(model_field == value)
    # 4. 如果有筛选条件，添加到查询语句中
    if filter_conditions:
        total_stmt = total_stmt.where(and_(*filter_conditions))
        list_stmt = list_stmt.where(and_(*filter_conditions))

    # 5. 分页
    list_stmt = list_stmt.offset(offset).limit(page_size).order_by(model.create_time.desc())

    # 6. 执行数据库查询（异步执行）
    # 获取总数
    total_result = await db.execute(total_stmt)
    total = total_result.scalar() or 0  # 提取总数的标量值

    # 获取列表数据
    list_result = await db.execute(list_stmt)
    model_instance_list = list_result.scalars().all() or []
    # 7. 返回结果
    return total, model_instance_list
