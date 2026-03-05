# 定义模型类
# 基类
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    这个是为了建表方便的基类，所有orm模型都必须继承这个类，才能正常建表。
    """
    pass
