# 1. 创建用户
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User
from schemas.users import UserCreate, UserUpdate


# 1. 创建用户
async def create_user(db: AsyncSession, user: UserCreate) -> User:
    db_user = User(
        username=user.username,
        password=user.password,  # 生产环境请先加密！
        real_name=user.real_name,
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


# 5. 查询所有用户（分页）
async def get_users(db: AsyncSession, skip: int = 0, limit: int = 10) -> List[User]:
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()


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
async def login(db: AsyncSession, username: str, password: str, role: int) -> Optional[User]:
    db_user = await get_user_by_username(db, username)
    if not db_user:
        return None
    if db_user.password != password:
        return None
    if db_user.role != role:
        return None
    return db_user
