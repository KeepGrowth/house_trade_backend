from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, DateTime, SmallInteger, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# 假设你的 Base 类、User 类和 House 类已经定义
from models.base import Base
from models.house_info import HouseInfo
from models.users import User


class Favorite(Base):
    __tablename__ = "house_favorite"  # 表名，可根据实际情况调整

    # 主键与外键
    favorite_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="收藏ID")
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user_info.user_id"),
        nullable=False,
        index=True,
        comment="收藏用户ID"
    )
    house_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("house_info.house_id"),
        nullable=False,
        index=True,
        comment="收藏房源ID"
    )

    # 收藏信息
    create_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, comment="收藏时间")
    is_deleted: Mapped[int] = mapped_column(SmallInteger, default=0, comment="0-正常收藏，1-取消收藏")

    # 关系映射
    user: Mapped["User"] = relationship("User", back_populates="favorites")
    house: Mapped["HouseInfo"] = relationship("House", back_populates="favorites")
