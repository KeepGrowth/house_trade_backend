from passlib.context import CryptContext

# 配置密码上下文：指定用bcrypt算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 将密码进行加密
def get_password_hash(password: str):
    hashed_password = pwd_context.hash(password)
    return hashed_password


# 验证密码
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
