from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.users import get_user_by_id
from models.base import HouseImage


# 新增房源图片
async def create_house_image(
        db: AsyncSession,
        house_id: int,
        image_url: str,
):
    db_house_image = HouseImage(
        house_id=house_id,
        image_url=image_url,
    )
    db.add(db_house_image)
    await db.commit()
    await db.refresh(db_house_image)
    return db_house_image
