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
    """
    if not params:
        params = {}

    # 1. 构建基础查询对象
    stmt = Select(Review)
    count_stmt = Select(func.count(Review.review_id))

    # 2. 动态拼接筛选条件
    if params.get('house_id'):
        stmt = stmt.where(Review.house_id == params['house_id'])
        count_stmt = count_stmt.where(Review.house_id == params['house_id'])

    if params.get('user_id'):
        stmt = stmt.where(Review.user_id == params['user_id'])
        count_stmt = count_stmt.where(Review.user_id == params['user_id'])

    if params.get('status'):
        stmt = stmt.where(Review.status == params['status'])
        count_stmt = count_stmt.where(Review.status == params['status'])

    # 3. 先查询总条数
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()  # 获取总数 (int)

    # 4. 处理分页
    page = int(params.get('page', 1))  # 默认第1页
    page_size = int(params.get('pageSize', 10))  # 默认每页10条

    # 计算偏移量: (页码 - 1) * 每页条数
    offset = (page - 1) * page_size

    stmt = stmt.offset(offset).limit(page_size).order_by(Review.create_time.desc())

    # 5. 查询列表数据
    result = await db.execute(stmt)
    reviews = result.scalars().all()

    return total, reviews


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
