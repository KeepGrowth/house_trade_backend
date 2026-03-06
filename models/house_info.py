from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, DateTime, DECIMAL, ForeignKey, Text, SmallInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from models.base import Base


class HouseInfo(Base):
    __tablename__ = "house_info"  # 表名，可根据实际情况调整

    # 主键与外键
    house_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="房源唯一ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_info.user_id"), nullable=False,
                                         comment="发布房源的用户ID")

    # 房源基本信息
    title: Mapped[str] = mapped_column(String(100), nullable=False, comment="房源标题")
    price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False, comment="房源总价（万元）")
    unit_price: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), comment="单价（元/㎡）")
    area: Mapped[float] = mapped_column(DECIMAL(6, 2), nullable=False, comment="建筑面积（㎡）")
    house_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="户型")
    floor: Mapped[Optional[str]] = mapped_column(String(20), comment="楼层信息")
    orientation: Mapped[Optional[str]] = mapped_column(String(10), comment="朝向")
    decoration: Mapped[Optional[str]] = mapped_column(String(20), comment="装修类型")

    # 位置信息
    community: Mapped[str] = mapped_column(String(50), nullable=False, index=True, comment="小区名称")
    district: Mapped[str] = mapped_column(String(30), nullable=False, index=True, comment="所在区域")
    address: Mapped[str] = mapped_column(String(255), nullable=False, comment="详细地址")
    build_year: Mapped[Optional[int]] = mapped_column(Integer, comment="建造年份")

    # 状态与描述
    sale_status: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1,
                                             comment="房源状态：1-在售，2-已售，3-已下架")
    description: Mapped[Optional[str]] = mapped_column(Text, comment="房源详细描述")

    # 时间戳
    create_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, comment="发布时间")
    update_time: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=datetime.now, comment="修改时间")

    # 反向映射
    user = relationship("User", back_populates="house_info")
    reviews = relationship("Review", back_populates="house_info")
    favorites = relationship("Favorite", back_populates="house_info")
