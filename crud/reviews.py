from sqlalchemy import Select
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
