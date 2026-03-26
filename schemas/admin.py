# ------------------------------
# Pydantic 模型（用于接口参数）
# ------------------------------
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field

from models.base import User


# 获取用户列表条件查询参数
class UserQueryParams(BaseModel):
    page: int = Field(None, alias="page")
    page_size: int = Field(None, alias="pageSize")
    role: Optional[int] = Field(None, alias="role")
    username: Optional[str] = Field(None, alias="username")
    model_config = ConfigDict(
        populate_by_name=True,  # alias 、字段名兼容
        from_attributes=True  # 允许从ORM对象属性中取值
    )


# 获取房源审核列表查询参数
class AuditParams(BaseModel):
    title: Optional[str] = Field(None, alias="title")
    audit_status: Optional[int] = Field(None, alias="auditStatus")
    page: int = Field(None, alias="page")
    page_size: int = Field(None, alias="pageSize")

    model_config = ConfigDict(
        populate_by_name=True,  # alias 、字段名兼容
        from_attributes=True  # 允许从ORM对象属性
    )
