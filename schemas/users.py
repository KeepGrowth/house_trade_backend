# ------------------------------
# Pydantic 模型（用于接口参数）
# ------------------------------
from datetime import datetime, date
from typing import Optional, List, Union

from pydantic import BaseModel, ConfigDict, Field

from models.base import User


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
    phone: str = Field(None, alias="phone")
    role: Optional[int] = Field(None, alias="role")
    avatar: Optional[str] = Field(None, alias="avatar")
    model_config = ConfigDict(
        populate_by_name=True,  # alias 、字段名兼容
        from_attributes=True  # 允许从ORM对象属性中取值
    )


class UsersQueryParams(BaseModel):
    page: Union[int, None] = Field(None, alias="page")
    page_size: Union[int, None] = Field(None, alias="pageSize")
    start_date: Optional[date] = Field(None, alias="startDate")
    end_date: Optional[date] = Field(None, alias="endDate")


class UserUpdate(BaseModel):
    user_id: Optional[int] = Field(None, alias="userId")
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
    phone: Optional[str] = Field(None, alias="phone")
    role: int = Field(None, alias="role")
    avatar: Optional[str] = Field(None, alias="avatar")
    create_time: Optional[datetime] = Field(None, alias="createTime")
    model_config = ConfigDict(
        populate_by_name=True,  # alias 、字段名兼容
        from_attributes=True  # 允许从ORM对象属性中取值
    )


# 用户列表信息
class UserListResponse(BaseModel):
    total: int = Field(None, alias="total")
    user_list: List[SafeUserResponse] = Field(None, alias="users")


# 用户令牌信息响应
class UserTokenResponse(BaseModel):
    token: str = Field(None, alias="token")
    user_info: SafeUserResponse = Field(None, alias="userInfo")
    model_config = ConfigDict(
        populate_by_name=True,  # alias 、字段名兼容
        from_attributes=True  # 允许从ORM对象属性中取值
    )
