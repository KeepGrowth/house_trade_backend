from sqlalchemy import Select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import Review


# 新增单个房源评价
async def create_house_review(
        db: AsyncSession,
        house_id: int,
        review_data: dict,
        user_id: int
):
    """
    新增单个房源评价
    :param db:
    :param house_id:
    :param review_data:
    :param user_id:
    :return:
    """
    review = Review(
        house_id=house_id,
        user_id=user_id,
        score=review_data.get("score"),
        content=review_data.get("content"),
        status=review_data.get("status")
    )
    db.add(review)
    await db.commit()
    return review


# 获取某个房源的评价列表
async def get_house_reviews(
        db: AsyncSession,
        house_id: int
):
    """
    获取某个房源的评价列表
    :param db:
    :param house_id:
    :return:
    """
    stmt = Select(Review).where(Review.house_id == house_id)
    reviews = await db.execute(stmt)
    return reviews.scalars().all()


# 条件查询评价列表
async def get_reviews(
        db: AsyncSession,
        params: dict = None
):
    """
    条件查询评价列表
    :param db:
    :param params:
    :return:
    """
    query = Select(Review)
    total_stmt = Select(func.count(Review.review_id))
    total = await db.execute(total_stmt)
    if params.get('house_id'):
        query = query.where(Review.house_id == params.get('house_id'))
        total = await db.execute(Select(Review).where(Review.house_id == params.get('house_id')))
    if params.get('user_id'):
        query = query.where(Review.user_id == params.get('user_id'))
        total = await db.execute(Select(Review).where(Review.user_id == params.get('user_id')))
    if params.get('status'):
        query = query.where(Review.status == params.get('status'))
        total = await db.execute(Select(Review).where(Review.status == params.get('status')))

    # 构建分页查询:page,page_size
    query = query.offset(params.get('page')).limit(params.get('pageSize'))
    query = query.order_by(Review.create_time.desc())
    reviews = await db.execute(query)
    return total.scalar_one(), reviews.scalars().all()


# 查询评价
async def get_review_by_id(
        db: AsyncSession,
        review_id: int
):
    """
    查询评价
    :param db:
    :param review_id:
    :return:
    """
    stmt = Select(Review).where(Review.review_id == review_id)
    review = await db.execute(stmt)
    return review.scalar_one_or_none()


# 删除评价
async def delete_review(
        db: AsyncSession,
        review_id: int
):
    """
    删除评价
    :param db:
    :param review_id:
    :return:
    """
    review = await get_review_by_id(db, review_id)
    await db.delete(review)
    await db.commit()
    return review


# 更新评价信息
async def update_review(
        db: AsyncSession,
        review_id: int,
        review_data: dict
):
    """
    更新评价信息
    :param db:
    :param review_id:
    :param review_data:
    :return:
    """
    review = await get_review_by_id(db, review_id)
    review.user_id = review_data.get("user_id")
    review.house_id = review_data.get("house_id")
    review.score = review_data.get("score")
    review.content = review_data.get("content")
    review.status = review_data.get("status")
    await db.commit()
    await db.refresh(review)
    return review
