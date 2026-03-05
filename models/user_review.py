from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, SmallInteger, Text, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from models.base import Base
from models.house_info import HouseInfo
from models.users import User


class Review(Base):
    __tablename__ = "user_review"  # 表名，可根据实际情况调整

    # 主键与外键
    review_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="评价ID")
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user_info.user_id"),
        nullable=False,
        index=True,
        comment="评价用户ID"
    )
    house_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("house_info.house_id"),
        nullable=False,
        index=True,
        comment="被评价房源ID"
    )

    # 评价内容
    score: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="评分（1-5星）")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="评价内容")

    # 状态与时间
    status: Mapped[int] = mapped_column(SmallInteger, default=1, comment="1-显示，0-隐藏/违规")
    create_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, comment="评价时间")

    # 关系映射
    user: Mapped["User"] = relationship("User", back_populates="reviews")
    house: Mapped["HouseInfo"] = relationship("House", back_populates="reviews")
