from sqlalchemy import func, Date, DateTime, String, Integer, ForeignKey, Column, SmallInteger
from typing import Optional
from config.mysql_config import Base, mapped_column, Mapped
from datetime import date, datetime


# 用户映射类基类
class UserBase(Base):
    __abstract__ = True
    create_time: Mapped[datetime] = mapped_column(DateTime, default=func.now(), comment="创建时间")
    update_time: Mapped[datetime] = mapped_column(DateTime, default=func.now(), comment="更新时间")


class User(Base):
    __tablename__ = "user_info"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="用户唯一ID")
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, comment="登录用户名")
    password: Mapped[str] = mapped_column(String(100), nullable=False, comment="登录密码（建议加密存储）")
    real_name: Mapped[Optional[str]] = mapped_column(String(20), comment="真实姓名")
    phone: Mapped[str] = mapped_column(String(11), nullable=False, unique=True, comment="联系电话")
    role: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1,
                                      comment="用户角色：1-普通用户/购房者，2-房东，3-管理员")
    avatar: Mapped[Optional[str]] = mapped_column(String(255), comment="用户头像地址")
    create_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, comment="注册时间")
    update_time: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=datetime.now, comment="信息修改时间")


# 用户-token类
class UserToken(Base):
    __tablename__ = "user_token"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="token_id")
    user_id: Mapped[int] = mapped_column(ForeignKey("user_info.user_id"), nullable=False, comment="用户id")
    token: Mapped[str] = mapped_column(String(500), nullable=False, comment="token")
    expires_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="过期时间")
    create_time: Mapped[datetime] = mapped_column(DateTime, default=func.now(), comment="创建时间")
