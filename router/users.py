from fastapi import APIRouter, Depends, HTTPException, status

from config.mysql_config import *
from crud.users import *
from schemas.users import *

# 导入你已有的模型、CRUD、Pydantic

# 创建路由
router = APIRouter(
    prefix="/api/users",
    tags=["用户管理"],
    responses={404: {"description": "未找到"}},
)


# ------------------------------
# RESTful API 接口
# ------------------------------

@router.post("/", summary="创建用户", status_code=status.HTTP_201_CREATED)
async def create_user_api(
        user: UserCreate,
        db: AsyncSession = Depends(get_database)
):
    """
    创建新用户
    - 用户名、手机号唯一
    - 密码建议加密存储
    """
    # 唯一性校验
    if await get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="用户名已存在")
    if await get_user_by_phone(db, user.phone):
        raise HTTPException(status_code=400, detail="手机号已注册")

    return await create_user(db, user)


@router.get("/", summary="获取用户列表（分页）")
async def get_users_api(
        skip: int = 0,
        limit: int = 10,
        db: AsyncSession = Depends(get_database)
):
    """分页获取用户列表"""
    return await get_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", summary="获取单个用户详情")
async def get_user_api(
        user_id: int,
        db: AsyncSession = Depends(get_database)
):
    """根据用户ID获取用户信息"""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.put("/{user_id}", summary="更新用户信息")
async def update_user_api(
        user_id: int,
        user_update: UserUpdate,
        db: AsyncSession = Depends(get_database)
):
    """
    更新用户信息
    - 只传需要修改的字段
    """
    user = await update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.delete("/{user_id}", summary="删除用户", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_api(
        user_id: int,
        db: AsyncSession = Depends(get_database)
):
    """删除指定用户"""
    success = await delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")
    return