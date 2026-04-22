# 1. 创建用户
from typing import List, Optional

from sqlalchemy import select, func, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import User
from schemas.users import UserCreate, UserUpdate
from utils.sql import common_query_list


# 1. 创建用户
async def create_user(db: AsyncSession, user: UserCreate) -> User:
    db_user = User(
        username=user.username,
        password=user.password,  # 生产环境请先加密！
        phone=user.phone,
        role=user.role,
        avatar=user.avatar
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


# 2. 根据ID查询用户
async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).where(User.user_id == user_id))
    return result.scalar_one_or_none()


# 3. 根据用户名查询用户
async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


# 4. 根据手机号查询用户
async def get_user_by_phone(db: AsyncSession, phone: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.phone == phone))
    return result.scalar_one_or_none()


# 查询所有用户
async def get_all_users(
        db: AsyncSession
):
    result = await db.execute(select(User))
    return result.scalars().all()


# 5. 查询所有用户（分页）
async def get_users(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        role: int = None,
        username: str = None
):
    """
    分页条件查询用户
    :param db:
    :param page:
    :param page_size:
    :param role: 角色
    :param username: 用户名
    :return:
    """
    query = select(User)
    if role:
        query = query.where(User.role == role)
    if username:
        query = query.where(User.username.like(f"%{username}%"))
    result = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
    total_query = select(func.count(User.user_id)).select_from(User)
    total = await db.execute(total_query)
    return total.scalar_one(), result.scalars().all()


# 条件查询-分页
async def query_users(
        db: AsyncSession,
        query_params: dict
):
    """
    条件查询用户数据-带分页。
    :param db:
    :param query_params:
    :return:
    """
    list_stmt = select(User)
    if query_params.get('start_date'):
        list_stmt = list_stmt.where(cast(User.create_time, Date) >= query_params.get('start_date'))
    if query_params.get('end_date'):
        list_stmt = list_stmt.where(cast(User.create_time, Date) <= query_params.get('end_date'))
    total_stmt = select(func.count(User.user_id))
    return await common_query_list(db, query_params, total_stmt, list_stmt, User)


# 6. 更新用户信息
async def update_user(db: AsyncSession, user_id: int, user_update: UserUpdate) -> Optional[User]:
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        return None

    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    await db.commit()
    await db.refresh(db_user)
    return db_user


# 7. 删除用户
async def delete_user(db: AsyncSession, user_id: int) -> bool:
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        return False

    await db.delete(db_user)
    await db.commit()
    return True


# 8. 用户登录
async def login(db: AsyncSession, username: str, password: str) -> Optional[User]:
    db_user = await get_user_by_username(db, username)
    if not db_user:
        return None
    if db_user.password != password:
        return None
    return db_user


# 9. 更新用户头像
async def update_user_avatar(db: AsyncSession, user_id: int, avatar: str) -> Optional[User]:
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        return None
    db_user.avatar = avatar
    await db.commit()
    await db.refresh(db_user)
    return db_user
