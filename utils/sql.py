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
    通用分页/全量查询方法
    逻辑：如果 query_params 中包含 page 或 page_size，则执行分页；否则查询所有符合条件的数据。
    """
    # 1. 定义允许的筛选字段白名单，防止非法字段注入
    mapper = inspect(model)
    # 获取模型的所有列名作为白名单
    allow_filter_keys = [key for key, value in mapper.columns.items()]

    # 2. 判断是否需要分页
    # 检查参数中是否存在 page 或 page_size 键
    has_pagination = 'page' in query_params or 'page_size' in query_params

    page = 1
    page_size = 10
    offset = 0

    if has_pagination:
        # --- 分页模式逻辑 ---
        # 获取页码
        page = query_params.get('page', 1)
        try:
            page = int(page)
            page = max(1, page)
        except (ValueError, TypeError):
            page = 1

        # 获取每页数量
        page_size = query_params.get('page_size', 10)
        try:
            page_size = int(page_size)
            page_size = min(page_size, 100)  # 限制最大每页数量
        except (ValueError, TypeError):
            page_size = 10

        # 计算偏移量
        offset = (page - 1) * page_size

    # 3. 清理分页参数，准备提取筛选条件
    # 无论是否分页，都移除这两个字段，防止它们被当作筛选条件
    query_params.pop('page', None)
    query_params.pop('page_size', None)

    # 4. 构建筛选条件
    filter_conditions = []
    for key, value in query_params.items():
        # 只处理白名单内的字段
        if key in allow_filter_keys:
            # 处理空值或列表等情况可根据需要扩展，这里保持原有的相等判断
            model_field = getattr(model, key)
            filter_conditions.append(model_field == value)

    # 5. 应用筛选条件到语句
    if filter_conditions:
        total_stmt = total_stmt.where(and_(*filter_conditions))
        list_stmt = list_stmt.where(and_(*filter_conditions))

    # 6. 处理排序和分页限制
    # 默认按创建时间倒序，无论是否分页通常都需要排序
    list_stmt = list_stmt.order_by(model.create_time.desc())

    if has_pagination:
        # 如果开启了分页，应用 limit 和 offset
        list_stmt = list_stmt.offset(offset).limit(page_size)

    # 7. 执行数据库查询
    total = 0
    model_instance_list = []

    if has_pagination:
        # --- 分页模式：需要查总数 ---
        total_result = await db.execute(total_stmt)
        total = total_result.scalar() or 0

        list_result = await db.execute(list_stmt)
        model_instance_list = list_result.scalars().all()
    else:
        # --- 全量模式：不需要查总数，直接查列表 ---
        # 注意：全量查询时，total 通常没有意义，或者等于 len(list)
        list_result = await db.execute(list_stmt)
        model_instance_list = list_result.scalars().all()
        total = len(model_instance_list)

    return total, model_instance_list
