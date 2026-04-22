from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


# 新增订单参数
class OrderAddRequest(BaseModel):
    seller_id: Optional[int] = Field(None, alias="sellerId")
    buyer_id: Optional[int] = Field(None, alias="buyerId")
    amount: Optional[float] = Field(None, alias="amount")
    model_config = ConfigDict(
        populate_by_name=True,  # alias 、字段名兼容
        from_attributes=True  # 允许从ORM对象属性中取值
    )


# 更新订单参数
class OrderUpdateRequest(BaseModel):
    id: Optional[int] = Field(None, alias="id")


# 查询订单参数
class OrderQueryParams(OrderUpdateRequest):
    page: Optional[int] = Field(1, alias="page")
    page_size: Optional[int] = Field(10, alias="pageSize")


# 单订单响应
class OrderItemResponse(OrderUpdateRequest):
    create_time: Optional[datetime] = Field(None, alias="createTime")
    update_time: Optional[datetime] = Field(None, alias="updateTime")


# 列表订单响应
class OrderListResponse(BaseModel):
    total: Optional[int] = Field(None, alias="total")
    orders: Optional[List[OrderItemResponse]] = Field(None, alias="orderList")
    model_config = ConfigDict(
        populate_by_name=True,  # alias 、字段名兼容
        from_attributes=True  # 允许从ORM对象属性中取值
    )
