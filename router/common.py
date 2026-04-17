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

