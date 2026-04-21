from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


class RepliesAddRequest(BaseModel):
    reply_id: Optional[int] = Field(None, alias="replyId")
    post_id: Optional[int] = Field(None, alias="postId")
    user_id: Optional[int] = Field(None, alias="userId")
    content: Optional[str] = Field(None)
    model_config = ConfigDict(
        populate_by_name=True,  # alias 、字段名兼容
        from_attributes=True  # 允许从ORM对象属性中取值
    )


class RepliesUpdateRequest(RepliesAddRequest):
    create_time: Optional[datetime] = Field(None, alias="createTime")
    update_time: Optional[datetime] = Field(None, alias="updateTime")


# 查询参数
class RepliesQueryParams(RepliesAddRequest):
    page: Optional[int] = Field(1, alias="page")
    page_size: Optional[int] = Field(10, alias="pageSize")


class RepliesResponse(RepliesAddRequest):
    create_time: Optional[datetime] = Field(None, alias="createTime")
    update_time: Optional[datetime] = Field(None, alias="updateTime")


class RepliesListResponse(BaseModel):
    replies: list[RepliesResponse] = Field(None, alias="replyList")
    total: int = Field(None, alias="total")
    model_config = ConfigDict(
        populate_by_name=True,  # alias 、字段名兼容
        from_attributes=True  # 允许从ORM对象属性中取值
    )
