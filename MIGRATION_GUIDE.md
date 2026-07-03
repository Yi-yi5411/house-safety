# 房屋安全鉴定系统 - 技术栈迁移指南

本项目已从原 **NestJS + React** 技术栈迁移为 **Python FastAPI + uniapp(Vue3)**。

---

## 项目架构

### 1. 后端 - Python FastAPI

```
backend/
├── app/
│   ├── main.py                 # FastAPI应用入口
│   ├── core/                   # 核心配置
│   │   ├── config.py           # 配置管理
│   │   ├── security.py         # JWT/安全工具
│   │   └── exceptions.py       # 自定义异常
│   ├── db/                     # 数据库
│   │   └── database.py         # SQLAlchemy配置
│   ├── models/                 # 数据模型
│   │   ├── user.py             # 用户模型
│   │   ├── survey.py           # 鉴定记录模型
│   │   ├── component_check.py  # 构件检查模型
│   │   └── ...                 # 其他模型
│   ├── schemas/                # Pydantic模型
│   │   ├── user.py             # 用户Schema
│   │   ├── survey.py           # 鉴定Schema
│   │   └── ...                 # 其他Schema
│   ├── api/                    # API路由
│   │   ├── v1/
│   │   │   ├── auth.py         # 认证路由
│   │   │   ├── surveys.py      # 鉴定路由
│   │   │   ├── components.py   # 构件路由
│   │   │   ├── ai.py           # AI路由
│   │   │   └── upload.py       # 上传路由
│   ├── services/               # 业务逻辑
│   │   ├── ai_service.py       # AI推理服务
│   │   └── ...                 # 其他服务
│   └── utils/                  # 工具函数
│       ├── sms.py              # 阿里云SMS
│       ├── wechat.py           # 微信登录
│       ├── oss.py              # 阿里云OSS
│       ├── ollama_client.py    # Ollama调用
│       └── redis_client.py     # Redis客户端
├── requirements.txt            # 依赖包
└── .env                        # 环境变量
```

### 2. 前端 - uniapp + Vue3 + ElementPlus

```
uniapp/
├── src/
│   ├── pages/                  # 页面
│   │   ├── login/              # 登录页
│   │   ├── index/              # 鉴定列表
│   │   ├── survey/             # 鉴定详情/表单
│   │   ├── component/          # 构件管理
│   │   ├── report/             # 报告预览
│   │   ├── ai/                 # AI助手
│   │   └── user/               # 个人中心
│   ├── components/             # 公共组件
│   ├── api/                    # API请求
│   │   ├── auth.ts             # 认证API
│   │   ├── survey.ts           # 鉴定API
│   │   ├── component.ts        # 构件API
│   │   └── ai.ts               # AI API
│   ├── stores/                 # Pinia状态管理
│   │   └── user.ts             # 用户状态
│   ├── utils/                  # 工具函数
│   │   └── request.ts          # HTTP请求封装
│   ├── App.vue                 # 应用入口
│   └── pages.json              # 页面配置
├── package.json                # 依赖包
└── vite.config.ts              # Vite配置
```

---

## 技术栈对比

| 组件 | 原技术栈 | 新技术栈 |
|------|---------|---------|
| 后端框架 | NestJS (TypeScript) | FastAPI (Python) |
| ORM | Drizzle | SQLAlchemy 2.0 |
| 数据库 | PostgreSQL | PostgreSQL |
| 缓存 | Redis | Redis |
| 前端框架 | React 19 | Vue 3 |
| 小程序 | - | uniapp |
| UI组件 | shadcn/ui | ElementPlus + uni-ui |
| 状态管理 | React Context | Pinia |
| 大模型调用 | 原方式 | LangChain + Ollama |
| 本地模型 | - | Qwen2.5:7b |
| 登录方式 | 内置登录 | 微信/手机号 |
| 文件存储 | 本地/云 | 阿里云OSS |

---

## 环境配置

### 1. 后端环境变量 (.env)

```bash
# 应用配置
DEBUG=true
APP_NAME="房屋安全鉴定系统"

# 数据库
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/house_safety

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b

# 微信登录
WECHAT_APP_ID=your-app-id
WECHAT_APP_SECRET=your-app-secret

# 阿里云OSS
OSS_ACCESS_KEY_ID=your-key-id
OSS_ACCESS_KEY_SECRET=your-key-secret
OSS_ENDPOINT=oss-cn-beijing.aliyuncs.com
OSS_BUCKET_NAME=your-bucket

# 阿里云SMS
ALIYUN_ACCESS_KEY_ID=your-key-id
ALIYUN_ACCESS_KEY_SECRET=your-key-secret
ALIYUN_SMS_SIGN_NAME=your-sign
```

### 2. 启动服务

```bash
# 1. 安装依赖
cd backend
pip install -r requirements.txt

# 2. 数据库迁移
alembic upgrade head

# 3. 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 4. 启动Ollama (本地模型)
ollama run qwen2.5:7b
```

### 3. 前端开发

```bash
cd uniapp
npm install

# H5开发
npm run dev:h5

# 微信小程序
npm run dev:mp-weixin
```

---

## API接口列表

### 认证接口
- `POST /api/v1/auth/sms/send` - 发送短信验证码
- `POST /api/v1/auth/sms/verify` - 验证短信码
- `POST /api/v1/auth/login/phone` - 手机号登录
- `POST /api/v1/auth/login/wechat` - 微信登录
- `POST /api/v1/auth/refresh` - 刷新Token

### 用户接口
- `GET /api/v1/users/me` - 获取当前用户
- `PUT /api/v1/users/me` - 更新用户信息

### 鉴定记录接口
- `GET /api/v1/surveys` - 列表（分页+搜索）
- `POST /api/v1/surveys` - 创建
- `GET /api/v1/surveys/{id}` - 详情
- `PUT /api/v1/surveys/{id}` - 更新
- `DELETE /api/v1/surveys/{id}` - 删除

### 构件检查接口
- `GET /api/v1/surveys/{id}/components` - 列表
- `POST /api/v1/surveys/{id}/components` - 创建
- `PUT /api/v1/components/{id}` - 更新
- `DELETE /api/v1/components/{id}` - 删除
- `POST /api/v1/surveys/{id}/components/batch` - 批量更新

### AI推理接口
- `POST /api/v1/ai/reasoning` - 执行AI推理
- `POST /api/v1/ai/generate-report` - 生成报告
- `POST /api/v1/ai/chat` - AI对话（流式）

### 文件上传接口
- `POST /api/v1/upload/image` - 上传图片
- `POST /api/v1/upload/file` - 上传文件

---

## 本地大模型配置

### 1. 安装Ollama

```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# 下载安装包: https://ollama.com/download/windows
```

### 2. 下载Qwen模型

```bash
# 下载Qwen2.5 7B模型
ollama pull qwen2.5:7b

# 验证模型
ollama run qwen2.5:7b
```

### 3. 配置环境变量

```bash
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=qwen2.5:7b
```

---

## 登录方式

### 手机号登录流程
1. 用户输入手机号
2. 点击"获取验证码"
3. 后端调用阿里云SMS发送验证码（存入Redis，5分钟有效）
4. 用户输入验证码
5. 后端验证通过后生成JWT Token
6. 前端存储Token，后续请求携带

### 微信登录流程
1. 用户点击"微信登录"
2. 小程序调用 `wx.login()` 获取code
3. 后端用code调用微信接口换取openid
4. 根据openid查询或创建用户
5. 生成JWT Token返回

---

## 图片存储

所有图片上传至阿里云OSS：
- 自动生成UUID文件名
- 支持私有/公共读权限
- 图片压缩和缩略图生成
- 上传后返回可访问URL

---

## 迁移说明

### 数据库迁移
- 原NestJS的Drizzle schema已转换为SQLAlchemy模型
- 数据库结构保持一致，无需数据迁移
- 使用Alembic进行数据库版本管理

### 功能对应关系
| 原功能 | 新实现 |
|-------|-------|
| NestJS Controller | FastAPI Router |
| NestJS Service | FastAPI Depends服务 |
| Drizzle ORM | SQLAlchemy 2.0 |
| React组件 | Vue3 SFC组件 |
| React Hooks | Vue3 Composition API |
| Context状态 | Pinia Store |
| 原AI调用 | LangChain + Ollama |

---

## 开发建议

1. **后端开发**
   - 使用 `async/await` 处理异步操作
   - 使用 Pydantic 进行数据验证
   - 使用依赖注入管理服务和数据库会话
   - 使用 Alembic 管理数据库迁移

2. **前端开发**
   - 使用 `<script setup>` 语法
   - 使用 Composition API 组织逻辑
   - 使用 Pinia 管理全局状态
   - 注意小程序和H5的兼容性差异

3. **AI功能**
   - 确保Ollama服务已启动
   - 首次加载模型可能需要等待
   - 可根据需要更换其他模型

---

## 注意事项

1. **环境依赖**
   - Python >= 3.10
   - Node.js >= 18
   - PostgreSQL >= 14
   - Redis >= 6
   - Ollama (本地模型)

2. **微信小程序**
   - 需要配置合法域名
   - 需要申请用户授权
   - 需要配置业务域名

3. **生产部署**
   - 使用 Gunicorn + Uvicorn 部署后端
   - 配置 Nginx 反向代理
   - 配置 HTTPS
   - 配置日志收集
