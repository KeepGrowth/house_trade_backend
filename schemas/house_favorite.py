# ------------------------------
# Pydantic 模型
# ------------------------------
from pydantic import BaseModel


class FavoriteCreate(BaseModel):
    user_id: int
    house_id: int