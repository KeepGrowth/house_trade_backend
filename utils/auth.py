import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Header, Depends, HTTPException
from starlette import status
from crud import users

from config.mysql_config import get_database
# jwt令牌
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from pydantic import BaseModel

# ===================== JWT 配置 =====================
SECRET_KEY = "house_price_trade_system"  # 改成你自己的密钥
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 7  # 7天有效期


# 生成 token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    生成7天的JWT令牌。
    :param data:
    :param expires_delta:
    :return:
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# 定义鉴权依赖
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# 获取当前登录用户
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无法获取到用户ID，请检查JWT令牌",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT令牌解析失败",
            headers={"WWW-Authenticate": "Bearer"},
        )
