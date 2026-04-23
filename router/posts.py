from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body

import utils.auth
from config.mysql_config import *
from crud.posts import *
from schemas.posts import *
from utils.response import *

# 创建路由
router = APIRouter(
    prefix="/posts",
    tags=["帖子模块"],
    responses={404: {"description": "未找到"}},
)


@router.get('/list')
async def get_posts_api(
        query_params: PostsQueryParams = Query(...),
        db: AsyncSession = Depends(get_database)
):
    """
    条件查询帖子列表
    :param query_params:
    :param db:
    :return:
    """
    total, posts_result = await query_posts(db, query_params.model_dump(exclude_unset=True, exclude_none=True))
    posts_list = [PostItemResponse().model_validate(post) for post in posts_result]
    res_data = PostListResponse(posts=posts_list, total=total)
    return success_response(message="获取成功", data=res_data)


@router.get('/detail/{post_id}')
async def get_post_detail_api(
        post_id: int,
        db: AsyncSession = Depends(get_database)
):
    """
    获取帖子详情
    :param post_id:
    :param db:
    :return:
    """
    post = await get_post_by_id(db, post_id)
    if not post:
        return error_response(message="帖子不存在")
    post = PostItemResponse().model_validate(post)
    return success_response(message="获取成功", data=post)


@router.post('/add')
async def add_post_api(
        post_data: PostAddRequest,
        db: AsyncSession = Depends(get_database),
        current_user_id: int = Depends(utils.auth.get_current_user),
):
    """
    添加帖子
    """
    try:
        post_data.user_id = current_user_id
        post = await add_post(db, post_data.model_dump(exclude_unset=True, exclude_none=True))
        if not post:
            return error_response(message="添加失败")
        post = PostItemResponse().model_validate(post)
        return success_response(message="添加成功", data=post)
    except Exception as e:
        return error_response(message='添加房源不存在' + str(e))


@router.put('/update')
async def update_post_api(
        post_data: PostUpdateRequest,
        db: AsyncSession = Depends(get_database),
        current_user_id: int = Depends(utils.auth.get_current_user),
):
    """
    更新帖子
    """
    post_data.user_id = current_user_id
    result = await update_post(db, post_data.model_dump(exclude_unset=True, exclude_none=True))
    if not result:
        return error_response(message="更新失败")
    return success_response(message="更新成功")


@router.delete('/delete/{post_id}')
async def delete_post_api(
        post_id: int = Path(...),
        db: AsyncSession = Depends(get_database),
        current_user_id: int = Depends(utils.auth.get_current_user),
):
    """
    删除帖子
    """
    result = await delete_post(db, post_id)
    if not result:
        return error_response(message="删除失败")
    return success_response(message="删除成功")


# 切换显示隐藏状态x`
@router.post("/switch_status", summary="切换显示隐藏状态", status_code=status.HTTP_200_OK)
async def switch_status_api(
        post_id: int = Body(..., title="评价ID", alias="postId"),
        current_user_id: int = Depends(utils.auth.get_current_user),
        db: AsyncSession = Depends(get_database)
):
    """切换显示隐藏状态"""
    post = await get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=400, detail="评价不存在")
    post.status = 1 if post.status == 0 else 0
    await db.commit()
    await db.refresh(post)
    return success_response(message="切换成功", data=PostItemResponse().model_validate(post))
