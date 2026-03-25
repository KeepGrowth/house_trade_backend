from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File

import utils.auth
from config.mysql_config import *
from crud.users import *
from schemas.users import *
from utils.response import *

# 导入你已有的模型、CRUD、Pydantic

# 创建路由
router = APIRouter(
    prefix="/common",
    tags=["公共模块"],
    responses={404: {"description": "未找到"}},
)


# 通用文件上传接口
@router.post("/upload", summary="通用文件上传接口", status_code=status.HTTP_200_OK)
async def upload_api(
        files: List[UploadFile] = File(...),
        current_user: User = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """通用文件上传接口"""
    urls = await upload_files(files)
    return success_response(message="上传成功", data=urls)
