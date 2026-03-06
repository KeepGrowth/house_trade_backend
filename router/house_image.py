from fastapi import APIRouter, Depends, HTTPException, status

from config.mysql_config import get_database
from crud.house_image import *
from utils.auth import get_current_user

router = APIRouter(
    prefix="/house-images",
    tags=["房源图片管理"],
    # 全局鉴权，非登录不可获取。
    dependencies=[Depends(get_current_user)]
)


# 上传图片
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_image(image: HouseImageCreate, db: AsyncSession = Depends(get_database)):
    return await create_house_image(db, image)


# 获取房源所有图片
@router.get("/house/{house_id}", response_model=List[HouseImageCreate])
async def get_images(house_id: int, db: AsyncSession = Depends(get_database)):
    return await get_house_images_by_house_id(db, house_id)


# 获取房源封面图
@router.get("/cover/{house_id}")
async def get_cover(house_id: int, db: AsyncSession = Depends(get_database)):
    img = await get_house_cover_image(db, house_id)
    if not img:
        raise HTTPException(status_code=404, detail="无封面图")
    return img


# 更新图片
@router.put("/{image_id}")
async def update_image(image_id: int, image: HouseImageUpdate, db: AsyncSession = Depends(get_database)):
    res = await update_house_image(db, image_id, image)
    if not res:
        raise HTTPException(status_code=404, detail="图片不存在")
    return res


# 删除图片
@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(image_id: int, db: AsyncSession = Depends(get_database)):
    if not await delete_house_image(db, image_id):
        raise HTTPException(status_code=404, detail="图片不存在")


# 清空房源所有图片
@router.delete("/house/{house_id}", status_code=status.HTTP_204_NO_CONTENT)
async def clear_images(house_id: int, db: AsyncSession = Depends(get_database)):
    await delete_house_images_by_house_id(db, house_id)
