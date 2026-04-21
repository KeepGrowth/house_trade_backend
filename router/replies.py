from fastapi import APIRouter, Depends, HTTPException, status, Query, Path

import utils.auth
from config.mysql_config import *
from crud.replies import *
from schemas.replies import *
from utils.response import *

# 创建路由
router = APIRouter(
    prefix="/replies",
    tags=["回复模块"],
    responses={404: {"description": "未找到"}},
)


@router.get('/list')
async def get_replies_api(
        query_params: RepliesQueryParams = Query(...),
        db: AsyncSession = Depends(get_database)
):
    """
    条件查询帖子列表
    :param query_params:
    :param db:
    :return:
    """
    total, replies_result = await query_replies(db, query_params.model_dump(exclude_unset=True, exclude_none=True))
    replies_list = [RepliesResponse().model_validate(replies) for replies in replies_result]
    res_data = RepliesListResponse(replies=replies_list, total=total)
    return success_response(message="获取成功", data=res_data)


@router.get('/detail/{replies_id}')
async def get_replies_detail_api(
        replies_id: int,
        db: AsyncSession = Depends(get_database)
):
    """
    获取帖子详情
    :param replies_id:
    :param db:
    :return:
    """
    replies = await get_replies_by_id(db, replies_id)
    if not replies:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子不存在")
    replies = RepliesResponse().model_validate(replies)
    return success_response(message="获取成功", data=replies)


@router.post('/add')
async def add_replies_api(
        replies_data: RepliesAddRequest,
        db: AsyncSession = Depends(get_database),
        current_user_id: int = Depends(utils.auth.get_current_user),
):
    """
    添加帖子
    """
    replies_data.user_id = current_user_id
    replies = await add_replies(db, replies_data.model_dump(exclude_unset=True, exclude_none=True))
    if not replies:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="添加失败")
    replies = RepliesResponse().model_validate(replies)
    return success_response(message="添加成功", data=replies)


@router.put('/update')
async def update_replies_api(
        replies_data: RepliesUpdateRequest,
        db: AsyncSession = Depends(get_database),
        current_user_id: int = Depends(utils.auth.get_current_user),
):
    """
    更新帖子
    """
    replies_data.user_id = current_user_id
    result = await update_replies(db, replies_data.model_dump(exclude_unset=True, exclude_none=True))
    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="更新失败")
    return success_response(message="更新成功")


@router.delete('/delete/{replies_id}')
async def delete_replies_api(
        replies_id: int = Path(...),
        db: AsyncSession = Depends(get_database),
        current_user_id: int = Depends(utils.auth.get_current_user),
):
    """
    删除帖子
    """
    result = await delete_replies(db, replies_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="删除失败")
    return success_response(message="删除成功")
