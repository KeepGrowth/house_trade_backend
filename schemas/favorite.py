# ------------------------------
# Pydantic 模型（用于接口参数）
# ------------------------------
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field

from models.base import House
from schemas.house import HouseResponse


# 单个收藏响应数据模型
class FavoriteResponse(BaseModel):
    favorite_id: Optional[int] = Field(None, alias="favoriteId")
    user_id: Optional[int] = Field(None, alias="userId")
    house_id: Optional[int] = Field(None, alias="houseId")
    create_time: Optional[datetime] = Field(None, alias="createTime")
    house: HouseResponse = Field(None, alias="house")
    house_images: Optional[List] = Field(None, alias="houseImages")

    model_config = ConfigDict(
        populate_by_name=True,  # alias 、字段名兼容
        from_attributes=True  # 允许从ORM对象属性中取值
    )


# 列表响应数据模型
class FavoriteListResponse(BaseModel):
    favorites: list[FavoriteResponse] = Field(None, alias="favorites")
    total: int = Field(None, alias="total")
    model_config = ConfigDict(
        populate_by_name=True,  # alias 、字段名兼容
        from_attributes=True  # 允许从ORM对象属性中取值
    )
