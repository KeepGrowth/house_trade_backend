# ------------------------------
# Pydantic 模型（用于接口参数）
# ------------------------------
from typing import Optional

from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    real_name: Optional[str] = None
    phone: str
    role: Optional[int] = 1
    avatar: Optional[str] = None


class UserUpdate(BaseModel):
    real_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[int] = None
    avatar: Optional[str] = None
    password: Optional[str] = None
