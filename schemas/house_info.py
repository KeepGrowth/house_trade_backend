# ------------------------------
# Pydantic 模型
# ------------------------------
from typing import Optional

from pydantic import BaseModel


class HouseCreate(BaseModel):
    user_id: int
    title: str
    price: float
    unit_price: Optional[float] = None
    area: float
    house_type: str
    floor: Optional[str] = None
    orientation: Optional[str] = None
    decoration: Optional[str] = None
    community: str
    district: str
    address: str
    build_year: Optional[int] = None
    sale_status: Optional[int] = 1
    description: Optional[str] = None

class HouseUpdate(BaseModel):
    title: Optional[str] = None
    price: Optional[float] = None
    unit_price: Optional[float] = None
    area: Optional[float] = None
    house_type: Optional[str] = None
    floor: Optional[str] = None
    orientation: Optional[str] = None
    decoration: Optional[str] = None
    community: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None
    build_year: Optional[int] = None
    sale_status: Optional[int] = None
    description: Optional[str] = None