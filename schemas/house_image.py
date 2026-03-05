# ------------------------------
# Pydantic 数据模型
# ------------------------------
from typing import Optional

from pydantic import BaseModel


class HouseImageCreate(BaseModel):
    """创建图片"""
    house_id: int
    image_url: str
    sort: Optional[int] = 0


class HouseImageUpdate(BaseModel):
    """更新图片（仅排序和地址可改）"""
    image_url: Optional[str] = None
    sort: Optional[int] = None
