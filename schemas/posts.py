# ------------------------------
# Pydantic 模型（用于接口参数）
# ------------------------------
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field

from schemas.house import HouseResponse
from schemas.replies import RepliesResponse
from schemas.users import SafeUserResponse


# 新增帖子数据模型
class PostAddRequest(BaseModel):
    user_id: Optional[int] = Field(None, alias="userId")
    house_id: Optional[int] = Field(None, alias="houseId")
    title: Optional[str] = Field(None)
    content: Optional[str] = Field(None, alias="content")
    status: Optional[int] = Field(None, alias="status")

    model_config = ConfigDict(
        populate_by_name=True,  # alias 、字段名兼容
        from_attributes=True  # 允许从ORM对象属性中取值
    )


# 更新参数
class PostUpdateRequest(PostAddRequest):
    post_id: Optional[int] = Field(None, alias="postId")


# 查询参数
class PostsQueryParams(PostAddRequest):
    page: Optional[int] = Field(1, alias="page")
    page_size: Optional[int] = Field(10, alias="pageSize")


# 单个帖子信息响应数据模型
class PostItemResponse(PostAddRequest):
    post_id: Optional[int] = Field(None, alias="postId")
    user: Optional[SafeUserResponse] = Field(None)
    house: Optional[HouseResponse] = Field(None)
    replies: Optional[List[RepliesResponse]] = Field(None)
    create_time: Optional[datetime] = Field(None, alias="createTime")
    update_time: Optional[datetime] = Field(None, alias="updateTime")


# 列表响应数据模型
class PostListResponse(BaseModel):
    posts: list[PostItemResponse] = Field(None, alias="postList")
    total: int = Field(None, alias="total")
    model_config = ConfigDict(
        populate_by_name=True,  # alias 、字段名兼容
        from_attributes=True  # 允许从ORM对象属性中取值
    )
