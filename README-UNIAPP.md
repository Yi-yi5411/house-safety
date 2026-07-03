# 房屋安全鉴定系统 - UniApp + FastAPI 版本

本项目是房屋安全鉴定系统的uni-app重构版本，采用Vue3 + FastAPI + LangChain技术栈。

## 技术架构

### 前端
- **框架**: uni-app (Vue3)
- **样式**: SCSS
- **HTTP客户端**: uni.request 封装
- **支持平台**: 微信小程序、H5

### 后端
- **框架**: FastAPI (Python 3.9+)
- **数据库**: PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **AI推理**: LangChain + Qwen3

## 项目结构

```
├── uniapp-backend/          # FastAPI后端
│   ├── app/
│   │   ├── api/v1/endpoints/  # API端点
│   │   │   ├── surveys.py      # 鉴定记录API
│   │   │   ├── component_checks.py  # 构件检查API
│   │   │   └── evaluation_standards.py  # 评定标准API
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py       # 应用配置
│   │   │   └── database.py     # 数据库连接
│   │   ├── models/            # 数据模型
│   │   │   └── models.py       # SQLAlchemy模型
│   │   ├── schemas/           # Pydantic模型
│   │   │   └── schemas.py      # 数据校验模型
│   │   ├── services/          # 业务服务层
│   │   │   ├── survey_service.py
│   │   │   ├── component_check_service.py
│   │   │   └── ai_service.py   # LangChain AI服务
│   │   └── main.py            # 应用入口
│   ├── scripts/               # 数据脚本
│   │   ├── init_db.py          # 初始化数据库
│   │   └── import_evaluation_standards.py  # 导入评定标准
│   ├── requirements.txt       # Python依赖
│   └── .env.example           # 环境变量示例
│
├── uniapp-frontend/         # uni-app前端
│   ├── pages/                 # 页面
│   │   ├── index/index.vue     # 鉴定列表
│   │   ├── survey/survey.vue   # 数据采集
│   │   ├── report/report.vue   # 报告预览
│   │   └── ai-assistant/       # AI助手
│   ├── utils/
│   │   └── request.js          # HTTP请求封装
│   ├── static/style/
│   │   └── common.scss         # 公共样式
│   ├── manifest.json          # 应用配置
│   ├── pages.json             # 页面路由
│   └── main.js                # 应用入口
│
└── README-UNIAPP.md          # 本文档
```

## 快速开始

### 1. 后端部署

```bash
# 进入后端目录
cd uniapp-backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接和AI模型

# 初始化数据库
python scripts/init_db.py --seed

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 前端开发

```bash
# 进入前端目录
cd uniapp-frontend

# 安装依赖
npm install

# H5开发
npm run dev:h5

# 微信小程序开发
npm run dev:mp-weixin
```

## API接口文档

启动后端后访问: http://localhost:8000/docs

### 主要接口

| 方法 | 路径 | 说明 |
|-----|------|------|
| GET | /api/v1/surveys | 获取鉴定列表 |
| POST | /api/v1/surveys | 创建鉴定记录 |
| GET | /api/v1/surveys/{id} | 获取鉴定详情 |
| PUT | /api/v1/surveys/{id} | 更新鉴定记录 |
| DELETE | /api/v1/surveys/{id} | 删除鉴定记录 |
| POST | /api/v1/surveys/{id}/ai-reasoning | AI推理 |
| GET | /api/v1/surveys/{survey_id}/component-checks | 获取构件检查 |
| POST | /api/v1/surveys/{survey_id}/component-checks | 创建构件检查 |
| PUT | /api/v1/component-checks/{id} | 更新构件检查 |
| DELETE | /api/v1/component-checks/{id} | 删除构件检查 |
| POST | /api/v1/surveys/{survey_id}/component-checks/batch | 批量更新 |
| GET | /api/v1/evaluation-standards | 获取评定标准 |

## 评定标准数据

数据库包含280条评定标准，覆盖：
- **地基基础**: 地基、基础 (19条)
- **上部承重结构**: 混凝土柱、砖柱、砖墙、混凝土梁、混凝土板、屋架 (106条)
- **围护结构**: 砌体自承重墙、门窗洞口过梁、挑梁、雨棚板、女儿墙 (71条)
- **其他**: 楼地面、屋面、非承重墙、门窗、外抹灰、内抹灰、顶棚、细木装修、水卫、电照、暖气、特种设备 (84条)

评定结果分级：
- 完好 (绿色)
- 基本完好 (蓝色)
- 一般损坏 (橙色)
- 严重损坏 (红色)
- 危险点 (深红色)

## AI推理配置

在 `.env` 文件中配置AI模型：

```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.example.com/v1
MODEL_NAME=qwen3
```

## 数据库模型

### Survey (鉴定记录)
- id: UUID
- address: 房屋地址
- build_year: 建造年代
- structure_type: 结构类型
- floor_count: 楼层数
- build_area: 建筑面积
- conclusion: 鉴定结论 (A/B/C/D级)
- basic_evaluation: 基础评定
- ai_reasoning_result: AI推理结果 (JSON)
- status: 状态 (draft/completed/exported)

### ComponentCheck (构件检查)
- id: UUID
- survey_id: 关联鉴定记录
- name: 构件名称
- category: 构件分类
- axis_line: 构件轴线
- checked_item_ids: 勾选的评定标准ID列表
- ai_evaluation_result: AI评定结果
- ai_evaluation_clause: AI评定条款
- photos: 照片URL列表

### EvaluationStandard (评定标准)
- id: UUID
- category: 构件分类
- component_type: 构件类型
- description: 查勘情况描述
- evaluation_result: 评定结果
- evaluation_clause: 评定标准条款
- sort_order: 排序

## 开发说明

### 新增评定标准

```bash
# 准备JSON数据文件 evaluation_data.json
# 格式: [{"category": "...", "component_type": "...", ...}]

# 导入数据
python scripts/import_evaluation_standards.py --file evaluation_data.json

# 或更新现有数据
python scripts/import_evaluation_standards.py --file evaluation_data.json --update
```

### 数据库迁移

```bash
# 重新创建所有表（会清空数据）
python scripts/init_db.py --drop-all

# 创建表并导入评定标准
python scripts/init_db.py --seed
```

## 部署建议

### 生产环境

1. 使用Docker部署PostgreSQL
2. 使用Gunicorn运行FastAPI
3. 配置Nginx反向代理
4. 配置HTTPS
5. 配置环境变量

### 微信小程序

1. 在manifest.json中配置appid
2. 在微信开发者工具中上传代码
3. 配置服务器域名（request合法域名）
4. 提交审核

## 开源协议

MIT License
