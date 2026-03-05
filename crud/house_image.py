from typing import Optional, List

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.house_image import HouseImage
from schemas.house_image import HouseImageCreate, HouseImageUpdate


# ------------------------------
# CRUD 核心方法
# ------------------------------

# 1. 创建房源图片
async def create_house_image(
    db: AsyncSession,
    image_in: HouseImageCreate
) -> HouseImage:
    db_image = HouseImage(**image_in.model_dump())
    db.add(db_image)
    await db.commit()
    await db.refresh(db_image)
    return db_image

# 2. 根据图片ID查询单张图片
async def get_house_image(
    db: AsyncSession,
    image_id: int
) -> Optional[HouseImage]:
    result = await db.execute(
        select(HouseImage).where(HouseImage.image_id == image_id)
    )
    return result.scalar_one_or_none()

# 3. 获取某个房源的所有图片（按 sort 排序）
async def get_house_images_by_house_id(
    db: AsyncSession,
    house_id: int
) -> List[HouseImage]:
    result = await db.execute(
        select(HouseImage)
        .where(HouseImage.house_id == house_id)
        .order_by(HouseImage.sort.asc())
    )
    return result.scalars().all()

# 4. 获取某个房源的封面图（sort=0）
async def get_house_cover_image(
    db: AsyncSession,
    house_id: int
) -> Optional[HouseImage]:
    result = await db.execute(
        select(HouseImage)
        .where(HouseImage.house_id == house_id)
        .where(HouseImage.sort == 0)
    )
    return result.scalar_one_or_none()

# 5. 更新图片信息（URL / 排序）
async def update_house_image(
    db: AsyncSession,
    image_id: int,
    image_update: HouseImageUpdate
) -> Optional[HouseImage]:
    db_image = await get_house_image(db, image_id)
    if not db_image:
        return None

    update_data = image_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_image, key, value)

    await db.commit()
    await db.refresh(db_image)
    return db_image

# 6. 删除单张图片
async def delete_house_image(
    db: AsyncSession,
    image_id: int
) -> bool:
    db_image = await get_house_image(db, image_id)
    if not db_image:
        return False

    await db.delete(db_image)
    await db.commit()
    return True

# 7. 删除某个房源的所有图片（批量删除）
async def delete_house_images_by_house_id(
    db: AsyncSession,
    house_id: int
) -> bool:
    await db.execute(
        delete(HouseImage).where(HouseImage.house_id == house_id)
    )
    await db.commit()
    return True