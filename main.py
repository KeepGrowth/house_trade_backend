import os

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from config.mysql_config import lifespan
from router import users, user_review, house_image, house_favorite, house_info

app = FastAPI(lifespan=lifespan)
# 路由注入
app.include_router(users.router)
app.include_router(user_review.router)
app.include_router(house_favorite.router)
app.include_router(house_info.router)
app.include_router(house_image.router)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 挂载uploads目录为静态文件目录，访问路径为 /images
app.mount("/images", StaticFiles(directory=UPLOAD_DIR), name="images")

# cors跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 允许访问的源，开发允许所有，生产环境需要指定。
    allow_credentials=True,  # 允许携带cookie
    allow_methods=["*"],  # 允许所有请求方法
    allow_headers=["*"],  # 允许所有请求头，token放置的地方。
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8086)
