from fastapi import APIRouter, Depends, HTTPException, status

import utils.auth
from config.mysql_config import *
from crud.users import *
from schemas.users import *
from utils.response import *

# 导入你已有的模型、CRUD、Pydantic

# 创建路由
router = APIRouter(
    prefix="/auth",
    tags=["认证模块"],
    responses={404: {"description": "未找到"}},
)


# ------------------------------
# RESTful API 接口
# ------------------------------
@router.post("/login", summary="用户登录", status_code=status.HTTP_200_OK)
async def login_api(
        user: UserLogin,
        db: AsyncSession = Depends(get_database)
):
    """用户登录"""
    user = await login(db, user.username, user.password)
    if not user:
        raise HTTPException(status_code=400, detail="用户名不存在或密码错误")
    token = utils.auth.create_access_token(data={"user_id": user.user_id})
    res_data = UserTokenResponse(token=token, user_info=SafeUserResponse().model_validate(user))
    return success_response(message="登录成功", data=res_data)


@router.post("/register", summary="用户注册", status_code=status.HTTP_200_OK)
async def register_api(
        user: UserCreate,
        db: AsyncSession = Depends(get_database)
):
    """用户注册"""
    # 唯一性校验
    if await get_user_by_username(db, user.username):
        return error_response(message="用户名已存在")
    if await get_user_by_phone(db, user.phone):
        return error_response(message="手机号已存在")
    new_user = await create_user(db, user)
    res_data = SafeUserResponse().model_validate(new_user)
    return success_response(message="注册成功", data=res_data)
