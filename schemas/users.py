# ------------------------------
# Pydantic 模型（用于接口参数）
# ------------------------------
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# 用户登录参数
class UserLogin(BaseModel):
    username: str
    password: str
    role: int = 1
    model_config = ConfigDict(
        populate_by_name=True,  # alias 、字段名兼容
        from_attributes=True  # 允许从ORM对象属性中取值
    )


class UserCreate(BaseModel):
    username: str
    password: str
    real_name: Optional[str] = Field(None, alias="realName")
    phone: str = Field(None, alias="phone")
    role: Optional[int] = Field(None, alias="role")
    avatar: Optional[str] = Field(None, alias="avatar")
    model_config = ConfigDict(
        populate_by_name=True,  # alias 、字段名兼容
        from_attributes=True  # 允许从ORM对象属性中取值
    )


class UserUpdate(BaseModel):
    real_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[int] = None
    avatar: Optional[str] = None
    password: Optional[str] = None
    model_config = ConfigDict(
        populate_by_name=True,  # alias 、字段名兼容
        from_attributes=True  # 允许从ORM对象属性中取值
    )


# 用户安全信息响应
class SafeUserResponse(BaseModel):
    user_id: int = Field(None, alias="userId")
    username: str = Field(None, alias="username")
    real_name: Optional[str] = Field(None, alias="realName")
    phone: str = Field(None, alias="phone")
    role: int = Field(None, alias="role")
    avatar: Optional[str] = Field(None, alias="avatar")
    model_config = ConfigDict(
        populate_by_name=True,  # alias 、字段名兼容
        from_attributes=True  # 允许从ORM对象属性中取值
    )


# 用户令牌信息响应
class UserTokenResponse(BaseModel):
    token: str = Field(None, alias="token")
    user_info: SafeUserResponse = Field(None, alias="userInfo")
    model_config = ConfigDict(
        populate_by_name=True,  # alias 、字段名兼容
        from_attributes=True  # 允许从ORM对象属性中取值
    )
