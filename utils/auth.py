from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Header, Depends, HTTPException
from starlette import status
from crud import users

from config.mysql_config import get_database


async def get_current_user(
        db: AsyncSession = Depends(get_database),
        authorization: str = Header(..., alias="Authorization")
):
    """
    用户token校验，返回用户。
    :param db:
    :param authorization:
    :return:
    """
    token = authorization.split(" ")[1]
    # 校验token
    user = await users.get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效|过期令牌")
    # 返回当前用户
    return user
