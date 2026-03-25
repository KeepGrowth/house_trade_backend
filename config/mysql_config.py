"""
系统mysql数据库配置项
"""

from datetime import datetime
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import DateTime, func, String
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from contextlib import asynccontextmanager
from fastapi import FastAPI
from models.base import Base

# ---------------------------------------需要先导入包，才能在lifespan中创建所有的数据库表---------------------------------
from models import base

# 数据库配置
ASYNC_DATABASE_URL = "mysql+aiomysql://root:mysql_bhjbrr@192.168.1.86:3306/house_price_trade_system"

# 创建异步引擎
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,  # 输出SQL日志；
    pool_size=10,  # 设置连接池中保持的持久连接数
    max_overflow=20,  # 设置连接池允许创建的额外连接数
)


# 创建数据库表
# 定义函数
async def create_tables():
    # 获取异步引擎，创建事务-建表
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # 使用模型类的元数据来创建


# 创建app实例的时候创建数据表
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动逻辑（等价于原来的 startup 事件）
    print("应用启动，初始化资源...")
    await create_tables()
    yield  # 应用运行期间
    # 关闭逻辑（等价于原来的 shutdown 事件）
    print("应用关闭，清理资源...")


# 将lifespan赋值给app实例。
# app = FastAPI(lifespan=lifespan)

# 异步会话窗口
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,  # 绑定数据库引擎
    class_=AsyncSession,  # 指定会话类
    expire_on_commit=False,  # 提交后会话不过期
)


# 依赖注入函数-用以跟数据库建立会话。
async def get_database():
    async with AsyncSessionLocal() as session:
        try:
            yield session  # 返回会话给路由处理函数
            await session.commit()  # 提交事物
        except Exception as e:
            await session.rollback()  # 异常事务回滚
            raise
        finally:
            await session.close()  # 关闭会话。
