# 1. 基础镜像：使用官方 Python 镜像，slim 版本体积更小
FROM python:3.11-slim

# 2. 设置工作目录
WORKDIR /app

# 3. 复制依赖文件并安装
# 先复制 requirements.txt 可以利用 Docker 缓存层，加快构建速度
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 4. 复制项目所有代码
COPY . .
RUN mkdir -p /app/uploads

# 5. 暴露端口 (视你的应用而定)
EXPOSE 8080

# 6. 启动命令 (如果 docker-compose 中没有指定 command，则使用此命令) uvicorn main:app --reload --port 8084
CMD ["uvicorn", "main:app" ,"--port","8080","--workers","4","--host","0.0.0.0"]