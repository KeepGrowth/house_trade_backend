# 二手房交易平台后端服务 (Second-Hand Housing Platform Backend)

基于 Python FastAPI 构建的高性能、高可用二手房交易后端系统，提供房源管理、用户认证、评价系统及后台审核等核心功能。

## 📋 项目简介

本项目是二手房交易平台的核心后端服务，采用 **Python 3.9.7 + FastAPI** 框架，配合 **MySQL 8.0** 数据库和 **Token** 身份验证机制。系统旨在为前端（Vue3）提供稳定、安全的 RESTful API 接口，支撑房源展示、搜索、发布、收藏、评价及管理员审核等全链路业务场景。

## 🚀 技术栈

- **开发语言**: Python 3.9.7
- **Web 框架**: FastAPI (异步高性能)
- **数据库**: MySQL 8.0
- **身份认证**: Token (JWT)
- **数据交互**: JSON
- **部署环境**: Linux / Docker (推荐)

## 🏗 系统架构与核心模块

系统采用模块化设计，主要包含以下核心业务模块：

### 1. 用户模块 (User Module)
- **功能**: 用户注册、登录、个人信息管理、角色权限控制。
- **核心表**: `用户信息表` (users)
- **角色体系**:
    - `1`: 普通用户/购房者
    - `2`: 房东 (可发布房源)
    - `3`: 管理员 (后台审核与管理)
- **特性**: 支持头像上传、真实姓名认证、联系方式管理。

### 2. 房源模块 (House Module)
- **功能**: 房源的发布、编辑、下架、详情查询、多条件筛选搜索。
- **核心表**: `房源信息表` (houses), `房源图片表` (house_images)
- **关键特性**:
    - 支持多图片上传与排序（含封面图设置）。
    - 丰富的房源属性：户型、朝向、装修、楼层、单价/总价自动计算。
    - 状态管理：在售、已售、已下架。
    - 地理位置索引：支持按区域、小区名称快速检索。

### 3. 互动与交易模块 (Interaction Module)
- **收藏功能**: 用户可收藏心仪房源，支持取消收藏。
    - 核心表：`房源收藏表` (favorites)
- **评价系统**: 用户对房源进行星级评分 (1-5星) 及文字评价。
    - 核心表：`用户评价表` (reviews)
    - 支持评价状态管理（显示/隐藏违规评价）。

### 4. 管理后台模块 (Admin Module)
- **功能**: 专为管理员角色设计，提供全局管控能力。
- **核心场景**:
    - **用户管理**: 用户列表查看、状态修改、批量操作。
    - **房源审核**: 对待审核房源进行“通过”或“驳回”操作，记录驳回原因。
    - **评价监管**: 审核用户评价，隐藏违规内容。

## 🗄️ 数据库设计概览

系统数据库设计遵循第三范式，核心实体关系如下：

| 表名 | 描述 | 关键字段 |
| :--- | :--- | :--- |
| `users` | 用户信息表 | `user_id`, `username`, `role`, `phone`, `avatar` |
| `houses` | 房源信息表 | `house_id`, `user_id`(FK), `price`, `area`, `district`, `sale_status` |
| `house_images` | 房源图片表 | `image_id`, `house_id`(FK), `image_url`, `sort` |
| `favorites` | 房源收藏表 | `favorite_id`, `user_id`(FK), `house_id`(FK), `is_deleted` |
| `reviews` | 用户评价表 | `review_id`, `user_id`(FK), `house_id`(FK), `score`, `content`, `status` |

> **注**: 所有时间字段 (`create_time`, `update_time`) 均统一使用 `DATETIME` 类型，确保数据追溯性。

## 🔌 主要 API 接口规划


- **认证相关**:
    - `POST /login`: 用户登录，返回 Token。
    - `POST /register`: 用户注册。
- **房源相关**:
    - `GET /house/list`: 获取房源列表（支持分页、区域、价格、户型筛选）。
    - `GET /house/detail/:houseId`: 获取房源详情（含图片列表、房东信息）。
    - `POST /publish/house`: 发布新房源（需房东权限）。
    - `PUT /publish/house/:houseId`: 编辑现有房源。
- **用户中心**:
    - `GET /user/center/my-house`: 获取我发布的房源。
    - `GET /user/center/favorite`: 获取我的收藏列表。
    - `POST /favorite/toggle`: 切换收藏状态。
- **评价相关**:
    - `GET /house/reviews/:houseId`: 获取某房源的评价列表。
    - `POST /review`: 提交新评价。
- **管理后台 (需 Admin 权限)**:
    - `GET /admin/house-audit`: 获取待审核房源列表。
    - `POST /admin/audit-action`: 执行审核操作（通过/驳回）。
    - `GET /admin/user`: 用户管理列表。

## 🛠️ 开发与运行指南

### 前置要求
- Python 3.9+
- MySQL 8.0+
- pip 或 poetry

### 安装依赖
```bash
pip install -r requirements.txt
```



### 启动服务
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 访问文档
启动后，可访问以下地址查看自动生成的 API 文档：
- Swagger UI: `http://localhost:8000/docs`


## 🔒 安全与权限

- **Token 验证**: 所有非公开接口（如发布房源、收藏、管理操作）均需携带有效的 JWT Token。
- **角色鉴权**: 接口内部根据 User Role (1/2/3) 进行细粒度权限控制，防止越权操作。
- **数据脱敏**: 敏感信息（如密码）加密存储，接口返回时自动过滤非必要隐私字段。

---
*本后端服务紧密配合前端 Vue3 + ElementPlus 架构，共同构成完整的二手房交易平台解决方案。*