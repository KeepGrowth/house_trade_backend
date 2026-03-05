# ------------------------------
# Pydantic 模型
# ------------------------------
from typing import Optional

from pydantic import BaseModel


class ReviewCreate(BaseModel):
    user_id: int
    house_id: int
    score: int  # 1-5
    content: str

class ReviewUpdate(BaseModel):
    score: Optional[int] = None
    content: Optional[str] = None
    status: Optional[int] = None  # 1显示 0隐藏