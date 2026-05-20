import os
import uuid

from fastapi import FastAPI, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from config.mysql_config import lifespan
from crud.house_images import create_house_image
from router import auth, users, houses, admin, reviews, dashboard, favorite, posts, replies
from utils.auth import get_current_user
from utils.response import success_response

app = FastAPI(lifespan=lifespan)
# 路由注入
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(houses.router)
app.include_router(admin.router)
app.include_router(reviews.router)
app.include_router(dashboard.router)
app.include_router(favorite.router)
app.include_router(posts.router)
app.include_router(replies.router)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
BASE_URL = "http://localhost:8086"
# 挂载uploads目录为静态文件目录，访问路径为 /images
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# cors跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://859707243.xyz:21353", "http://localhost:8000"],
    # 允许访问的源，开发允许所有，生产环境需要指定。
    allow_credentials=True,  # 允许携带cookie
    allow_methods=["*"],  # 允许所有请求方法
    allow_headers=["*"],  # 允许所有请求头，token放置的地方。
)
ALLOWED_EXTENSIONS = {"image/jpeg", "image/png", "image/gif", "image/webp"}


@app.get("/")
async def root():
    return {"message": "Hello World"}


# 头像上传接口
@app.post("/upload/avatar")
async def upload_avatar(
        db: AsyncSession = Depends(users.get_database),
        file: UploadFile = File(...),
        current_user: int = Depends(get_current_user)
):
    # 1. 校验文件类型
    if file.content_type not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file.content_type}。仅允许: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    contents = await file.read()

    # 3. 生成唯一文件名，防止覆盖
    ext = file.filename.split(".")[-1] if "." in file.filename else "png"
    unique_filename = f"{current_user}_{uuid.uuid4().hex}.{ext}"
    file_path = f"{UPLOAD_DIR}/{unique_filename}"
    print(file_path)

    # 4. 保存文件 (异步写入)
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")

    # 5. 构建返回给前端的 URL
    # 前端 el-upload 的 on-success 会接收这个 JSON
    file_url = f"{BASE_URL}/{file_path}"

    # 更新用户头像
    await users.update_user_avatar(db, current_user, avatar=file_url)

    return success_response(message="上传成功", data={
        "url": file_url,
        "filename": unique_filename
    })


# 房屋图片上传接口
@app.post("/upload/image")
async def upload_image(
        db: AsyncSession = Depends(users.get_database),
        file: UploadFile = File(...),
        current_user: int = Depends(get_current_user)
):
    # 1. 校验文件类型
    if file.content_type not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file.content_type}。仅允许: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    contents = await file.read()

    # 3. 生成唯一文件名，防止覆盖
    ext = file.filename.split(".")[-1] if "." in file.filename else "png"
    unique_filename = f"{current_user}_{uuid.uuid4().hex}.{ext}"
    file_path = f"{UPLOAD_DIR}/{unique_filename}"

    # 4. 保存文件 (异步写入)
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")

    # 5. 构建返回给前端的 URL
    # 前端 el-upload 的 on-success 会接收这个 JSON
    file_url = f"{BASE_URL}/{file_path}"

    # 新增到数据库中
    # await create_house_image(db,house_id=,image_url=file_url)

    return success_response(message="上传成功", data={
        "url": file_url,
        "filename": unique_filename
    })


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8080)
