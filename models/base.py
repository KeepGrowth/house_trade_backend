# 定义模型类
# 基类
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    这个是为了建表方便的基类，所有orm模型都必须继承这个类，才能正常建表。
    """
    pass


from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Column, Integer, String, DECIMAL, DateTime, ForeignKey,
    Text, SmallInteger, Boolean
)
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column


# 定义基类
class Base(DeclarativeBase):
    pass


# 1. 用户信息表 (users)
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True, comment="用户ID")
    username = Column(String(50), unique=True, nullable=False, comment="登录账号")
    password = Column(String(100), nullable=False, comment="加密后的密码")
    role = Column(SmallInteger, nullable=False, default=1, comment="角色：1-购房者, 2-房东, 3-管理员")
    phone = Column(String(11), comment="联系电话")
    avatar = Column(String(255), comment="头像URL")
    create_time = Column(DateTime, default=datetime.now, comment="注册时间")

    # --- 反向映射关系 ---
    # 一个用户发布多个房源 (针对房东)
    houses: Mapped[List["House"]] = relationship("House", back_populates="owner", foreign_keys="House.user_id")

    # 一个用户收藏多个房源
    favorites: Mapped[List["Favorite"]] = relationship("Favorite", back_populates="user")

    # 一个用户发表多条评价
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="user")

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username='{self.username}', role={self.role})>"


# 2. 房源信息表 (houses)
class House(Base):
    __tablename__ = "houses"

    house_id = Column(Integer, primary_key=True, autoincrement=True, comment="房源ID")
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, comment="关联发布者ID")
    title = Column(String(100), nullable=False, comment="房源标题")
    price = Column(DECIMAL(10, 2), nullable=False, comment="总价（万元）")
    area = Column(DECIMAL(6, 2), nullable=False, comment="面积（㎡）")
    house_type = Column(String(20), comment="户型（如：3室2厅）")
    district = Column(String(30), comment="所在区域")
    community = Column(String(50), comment="小区名称")
    sale_status = Column(SmallInteger, default=1, comment="状态：1-在售, 2-已售, 3-已下架")
    audit_status = Column(SmallInteger, default=0, comment="审核状态：0-待审, 1-通过, 2-驳回")
    # 补充创建时间，方便排序，虽然文档未明确列出但通常需要
    create_time = Column(DateTime, default=datetime.now)

    # --- 反向映射关系 ---
    # 关联到用户 (多对一)
    owner: Mapped["User"] = relationship("User", back_populates="houses", foreign_keys=[user_id])

    # 一个房源有多张图片
    images: Mapped[List["HouseImage"]] = relationship("HouseImage", back_populates="house",
                                                      cascade="all, delete-orphan",lazy="selectin")

    # 一个房源被多个用户收藏
    favorited_by: Mapped[List["Favorite"]] = relationship("Favorite", back_populates="house",
                                                          cascade="all, delete-orphan")

    # 一个房源有多条评价
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="house", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<House(house_id={self.house_id}, title='{self.title}', price={self.price})>"


# 3. 房源图片表 (house_images)
class HouseImage(Base):
    __tablename__ = "house_images"

    image_id = Column(Integer, primary_key=True, autoincrement=True, comment="图片ID")
    house_id = Column(Integer, ForeignKey("houses.house_id"), nullable=False, comment="关联房源ID")
    image_url = Column(String(255), nullable=False, comment="图片URL")
    sort = Column(Integer, default=0, comment="排序")

    # --- 反向映射关系 ---
    house: Mapped["House"] = relationship("House", back_populates="images")

    def __repr__(self):
        return f"<HouseImage(image_id={self.image_id}, house_id={self.house_id})>"


# 4. 房源收藏表 (favorites)
class Favorite(Base):
    __tablename__ = "favorites"

    favorite_id = Column(Integer, primary_key=True, autoincrement=True, comment="收藏ID")
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, comment="关联用户ID")
    house_id = Column(Integer, ForeignKey("houses.house_id"), nullable=False, comment="关联房源ID")
    create_time = Column(DateTime, default=datetime.now, comment="收藏时间")

    # --- 反向映射关系 ---
    user: Mapped["User"] = relationship("User", back_populates="favorites")
    house: Mapped["House"] = relationship("House", back_populates="favorited_by")

    def __repr__(self):
        return f"<Favorite(user_id={self.user_id}, house_id={self.house_id})>"


# 5. 用户评价表 (reviews)
class Review(Base):
    __tablename__ = "reviews"

    review_id = Column(Integer, primary_key=True, autoincrement=True, comment="评价ID")
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, comment="关联用户ID")
    house_id = Column(Integer, ForeignKey("houses.house_id"), nullable=False, comment="关联房源ID")
    score = Column(SmallInteger, nullable=False, comment="评分 1-5星")
    content = Column(Text, comment="评价内容")
    status = Column(SmallInteger, default=1, comment="是否显示：1-显示, 0-隐藏")
    create_time = Column(DateTime, default=datetime.now, comment="评价时间")

    # --- 反向映射关系 ---
    user: Mapped["User"] = relationship("User", back_populates="reviews")
    house: Mapped["House"] = relationship("House", back_populates="reviews")

    def __repr__(self):
        return f"<Review(review_id={self.review_id}, score={self.score})>"
