# ------------------------------
# CRUD 核心方法
# ------------------------------
from typing import Optional, List

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models.user_review import Review
from schemas.user_review import ReviewCreate, ReviewUpdate


# 创建评价
async def create_review(db: AsyncSession, review_in: ReviewCreate) -> Review:
    db_review = Review(**review_in.model_dump())
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)
    return db_review


# 根据ID获取评价
async def get_review_by_id(db: AsyncSession, review_id: int) -> Optional[Review]:
    result = await db.execute(
        select(Review).where(Review.review_id == review_id)
    )
    return result.scalar_one_or_none()


# 获取某个房源的所有有效评价（status=1）
async def get_reviews_by_house(
        db: AsyncSession,
        house_id: int,
        skip: int = 0,
        limit: int = 10
) -> List[Review]:
    result = await db.execute(
        select(Review)
        .where(and_(Review.house_id == house_id, Review.status == 1))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


# 获取某个用户的所有评价
async def get_reviews_by_user(
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 10
) -> List[Review]:
    result = await db.execute(
        select(Review)
        .where(Review.user_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


# 更新评价
async def update_review(
        db: AsyncSession,
        review_id: int,
        review_update: ReviewUpdate
) -> Optional[Review]:
    db_review = await get_review_by_id(db, review_id)
    if not db_review:
        return None

    update_data = review_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_review, key, value)

    await db.commit()
    await db.refresh(db_review)
    return db_review


# 删除/隐藏评价
async def delete_review(db: AsyncSession, review_id: int) -> bool:
    db_review = await get_review_by_id(db, review_id)
    if not db_review:
        return False

    # 软删除：改为隐藏
    db_review.status = 0
    await db.commit()
    return True
