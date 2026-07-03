# 房屋安全鉴定系统 - FastAPI 后端

## 技术栈

- **框架**: FastAPI 0.104.1
- **数据库**: PostgreSQL + SQLAlchemy 2.0 + Alembic
- **缓存**: Redis
- **认证**: JWT + OAuth2
- **大模型**: LangChain + Ollama (本地部署 Qwen3.5)
- **文件存储**: 阿里云OSS
- **短信**: 阿里云SMS
- **微信登录**: 微信小程序登录

## 项目结构

```
fastapi-backend/
├── app/
│   ├── api/
│   │   ├── deps.py              # 依赖注入
│   │   └── v1/
│   │       ├── api.py           # 路由聚合
│   │       └── endpoints/       # API端点
│   │           ├── auth.py      # 认证
│   │           ├── users.py     # 用户
│   │           ├── surveys.py   # 鉴定记录
│   │           ├── components.py # 构件
│   │           ├── ai.py        # AI推理
│   │           └── upload.py    # 文件上传
│   ├── core/
│   │   ├── config.py            # 配置
│   │   ├── security.py          # 安全工具
│   │   └── exceptions.py        # 自定义异常
│   ├── db/
│   │   └── database.py          # 数据库连接
│   ├── models/                  # SQLAlchemy模型
│   ├── schemas/                 # Pydantic模型
│   ├── services/                # 业务逻辑
│   └── utils/                   # 工具函数
├── alembic/                     # 数据库迁移
├── logs/                        # 日志目录
├── requirements.txt
├── .env.example
└── README.md
```

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库、Redis、OSS等
```

### 4. 数据库迁移

```bash
# 初始化迁移（首次）
alembic init alembic

# 创建迁移
alembic revision --autogenerate -m "init"

# 执行迁移
alembic upgrade head
```

### 5. 启动服务

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Ollama 本地模型配置

### 1. 安装 Ollama

```bash
# macOS
curl -fsSL https://ollama.com/install.sh | sh

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# 下载安装包: https://ollama.com/download/windows
```

### 2. 下载 Qwen3.5 模型

```bash
ollama pull qwen2.5:7b
```

### 3. 启动 Ollama 服务

```bash
ollama serve
```

### 4. 测试模型

```bash
ollama run qwen2.5:7b
```

## API 文档

启动服务后访问：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 主要 API 列表

| 方法 | 路径 | 说明 |
|-----|------|-----|
| POST | /api/v1/auth/login/phone | 手机号登录 |
| POST | /api/v1/auth/login/wechat | 微信登录 |
| GET | /api/v1/users/me | 当前用户 |
| GET | /api/v1/surveys | 鉴定列表 |
| POST | /api/v1/surveys | 创建鉴定 |
| GET | /api/v1/surveys/{id} | 鉴定详情 |
| PUT | /api/v1/surveys/{id} | 更新鉴定 |
| DELETE | /api/v1/surveys/{id} | 删除鉴定 |
| POST | /api/v1/ai/reason | AI推理 |
| POST | /api/v1/upload/image | 图片上传 |

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t house-safety-backend .

# 运行容器
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://... \
  -e REDIS_URL=redis://... \
  --name house-safety-backend \
  house-safety-backend
```

### 使用 Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - db
      - redis
      
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=house_safety
    volumes:
      - postgres_data:/var/lib/postgresql/data
      
  redis:
    image: redis:7-alpine
    
volumes:
  postgres_data:
```

## 微信登录配置

1. 在微信公众平台注册小程序
2. 获取 AppID 和 AppSecret
3. 在 `.env` 中配置:
   ```
   WECHAT_APP_ID=your_app_id
   WECHAT_APP_SECRET=your_app_secret
   ```

## 阿里云配置

### OSS 对象存储

1. 开通阿里云 OSS 服务
2. 创建 Bucket
3. 配置 AccessKey
4. 在 `.env` 中配置相关参数

### 短信服务

1. 开通阿里云短信服务
2. 申请短信签名和模板
3. 在 `.env` 中配置相关参数

## 开发规范

- 遵循 PEP 8 编码规范
- 使用类型注解
- 添加必要的注释
- 异常处理完善

## 许可证

MIT License
