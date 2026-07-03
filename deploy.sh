#!/bin/bash

# 房屋安全鉴定系统部署脚本
# 使用方法: ./deploy.sh [dev|prod]

set -e

ENV=${1:-dev}
echo "开始部署环境: $ENV"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    print_status "检查依赖..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "未找到 Python3，请先安装"
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        print_error "未找到 Node.js，请先安装"
        exit 1
    fi
    
    if ! command -v ollama &> /dev/null; then
        print_warning "未找到 Ollama，将使用远程模型或跳过AI功能"
    fi
    
    print_status "依赖检查完成"
}

# 部署后端
deploy_backend() {
    print_status "部署后端服务..."
    
    cd fastapi-backend
    
    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        print_status "创建虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 安装依赖
    print_status "安装后端依赖..."
    pip install -q -r requirements.txt
    
    # 检查环境变量
    if [ ! -f ".env" ]; then
        print_warning "未找到 .env 文件，使用默认配置"
        cp .env.example .env
    fi
    
    # 数据库迁移
    print_status "执行数据库迁移..."
    alembic upgrade head
    
    # 启动服务（后台）
    print_status "启动后端服务..."
    if [ "$ENV" = "prod" ]; then
        nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 > logs/server.log 2>&1 &
    else
        nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > logs/server.log 2>&1 &
    fi
    
    cd ..
    print_status "后端部署完成，服务运行在 http://localhost:8000"
}

# 部署前端
deploy_frontend() {
    print_status "部署前端..."
    
    cd uniapp-frontend
    
    # 安装依赖
    if [ ! -d "node_modules" ]; then
        print_status "安装前端依赖..."
        npm install
    fi
    
    # 构建H5
    print_status "构建H5..."
    npm run build:h5
    
    # 构建微信小程序
    print_status "构建微信小程序..."
    npm run build:mp-weixin
    
    cd ..
    print_status "前端构建完成"
    print_status "H5构建目录: uniapp-frontend/dist/build/h5"
    print_status "微信小程序构建目录: uniapp-frontend/dist/build/mp-weixin"
}

# 启动Ollama
start_ollama() {
    if command -v ollama &> /dev/null; then
        print_status "检查Ollama服务..."
        
        # 检查Ollama是否运行
        if ! pgrep -x "ollama" > /dev/null; then
            print_status "启动Ollama服务..."
            ollama serve &
            sleep 5
        fi
        
        # 检查模型是否存在
        if ! ollama list | grep -q "qwen2.5"; then
            print_status "下载Qwen模型（首次需要较长时间）..."
            ollama pull qwen2.5:7b
        fi
        
        print_status "Ollama服务就绪"
    fi
}

# 主函数
main() {
    echo "================================"
    echo "房屋安全鉴定系统部署脚本"
    echo "================================"
    
    check_dependencies
    
    # 创建必要的目录
    mkdir -p fastapi-backend/logs
    mkdir -p uniapp-frontend/dist
    
    # 启动Ollama
    start_ollama
    
    # 部署后端
    deploy_backend
    
    # 部署前端
    deploy_frontend
    
    echo ""
    echo "================================"
    print_status "部署完成！"
    echo "================================"
    echo ""
    echo "访问地址:"
    echo "  - 后端API: http://localhost:8000"
    echo "  - API文档: http://localhost:8000/docs"
    echo "  - H5前端: uniapp-frontend/dist/build/h5"
    echo ""
    echo "微信小程序:"
    echo "  使用微信开发者工具打开: uniapp-frontend/dist/build/mp-weixin"
    echo ""
}

# 运行主函数
main
