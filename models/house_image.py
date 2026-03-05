from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from models.base import Base


class HouseImage(Base):
    __tablename__ = "house_image"  # 表名，可根据实际情况调整

    # 主键与外键
    image_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="图片ID")
    house_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("house_info.house_id"),
        nullable=False,
        index=True,
        comment="关联房源ID"
    )

    # 图片信息
    image_url: Mapped[str] = mapped_column(String(255), nullable=False, comment="图片存储地址")
    sort: Mapped[int] = mapped_column(Integer, default=0, comment="图片排序（0为封面图）")

    # 时间戳
    create_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, comment="上传时间")
