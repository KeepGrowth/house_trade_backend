import os

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File

import utils.auth
from config.mysql_config import *
from crud.users import *
from schemas.users import *
from utils.response import *

# 导入你已有的模型、CRUD、Pydantic

# 创建路由
router = APIRouter(
    prefix="/reviews",
    tags=["评价模块"],
    responses={404: {"description": "未找到"}},
)


# 删除自己的评价
@router.delete("/{review_id}", summary="删除自己的评价", status_code=status.HTTP_200_OK)
async def delete_review_api(
        review_id: int,
        current_user: User = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """删除自己的评价"""
    review = await get_review_by_id(db, review_id)
    if not review:
        raise HTTPException(status_code=400, detail="评价不存在")
    if review.user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail="无权限")
    await delete_review(db, review_id)
    return success_response(message="删除成功")
