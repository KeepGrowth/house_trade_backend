# ------------------------------
# Pydantic 模型（用于接口参数）
# ------------------------------
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field

from models.base import House, HouseImage


# 新增房源信息数据模型
class HouseCreate(BaseModel):
    house_id: Optional[int] = Field(None, alias="houseId")
    user_id: Optional[int] = Field(None, alias="userId")
    title: Optional[str] = Field(None, alias="title")
    price: Optional[float] = Field(None, alias="price")
    area: Optional[float] = Field(None, alias="area")
    house_type: Optional[str] = Field(None, alias="houseType")
    district: Optional[str] = Field(None, alias="district")
    community: Optional[str] = Field(None, alias="community")
    sale_status: Optional[int] = Field(None, alias="saleStatus")
    audit_status: Optional[int] = Field(None, alias="auditStatus")

    # 图片列表
    image_urls: Optional[List] = Field(None, alias="imageUrls")

    model_config = ConfigDict(
        populate_by_name=True,  # alias 、字段名兼容
        from_attributes=True  # 允许从ORM对象属性中取值
    )


# 房源图片相应数据
class HouseImageReponse(BaseModel):
    image_id: Optional[int] = Field(None, alias="imageId")
    house_id: Optional[int] = Field(None, alias="houseId")
    image_url: Optional[str] = Field(None, alias="imageUrl")

    model_config = ConfigDict(
        populate_by_name=True,  # alias
        from_attributes=True
    )


# 房源信息响应数据模型
class HouseResponse(HouseCreate):
    create_time: Optional[datetime] = Field(None, alias="createTime")
    seller_info: Optional[dict] = Field(None, alias="sellerInfo")
    review_info: Optional[List] = Field(None, alias="reviewInfo")
    images: Optional[List[HouseImageReponse]] = Field(None, alias="imageUrls")

    model_config = ConfigDict(
        populate_by_name=True,  # alias 、字段名兼容
        from_attributes=True  # 允许从ORM对象属性中取值
    )


# 房源信息列表响应数据模型
class HouseListResponse(BaseModel):
    houses: list[HouseResponse] = Field(None, alias="houses")
    total: int = Field(None, alias="total")
    model_config = ConfigDict(
        populate_by_name=True,  # alias 、字段名兼容
        from_attributes=True  # 允许从ORM对象属性中取值
    )


# 房源审核状态响应数据模型
class HouseAuditStatusResponse(BaseModel):
    house_id: Optional[int] = Field(None, alias="houseId")
    audit_status: Optional[int] = Field(None, alias="auditStatus")

    model_config = ConfigDict(
        populate_by_name=True,  # alias 、字段名兼容
        from_attributes=True  # 允许从ORM对象属性中取值
    )
