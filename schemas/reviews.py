# ------------------------------
# Pydantic 模型（用于接口参数）
# ------------------------------
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from crud.users import get_user_by_id


# 新增评价Request模型
class ReviewCreate(BaseModel):
    review_id: Optional[int] = Field(None, alias="reviewId")
    user_id: Optional[int] = Field(None, alias="userId")
    house_id: Optional[int] = Field(None, alias="houseId")
    score: Optional[float] = Field(None, alias="score")
    content: Optional[str] = Field(None, alias="content")
    status: Optional[int] = Field(None, alias="status")
    model_config = ConfigDict(
        populate_by_name=True,  # alias 、字段名兼容
        from_attributes=True  # 允许从ORM对象属性中取值
    )


# 评价Response模型
class ReviewResponse(ReviewCreate):
    create_time: Optional[datetime] = Field(None, alias="createTime")


# 评价列表Response模型
class ReviewListResponse(BaseModel):
    reviews: list[ReviewResponse] = Field(None, alias="reviews")
    total: int = Field(None, alias="total")
    model_config = ConfigDict(
        populate_by_name=True,  # alias 、字段名兼容
        from_attributes=True  # 允许从ORM对象属性中取值
    )
