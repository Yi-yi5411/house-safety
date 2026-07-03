@echo off
chcp 65001 >nul
echo ============================================
echo   房屋安全鉴定系统 - 一键启动 (Docker)
echo ============================================
echo.

cd /d "%~dp0"

echo [1/2] 停止旧容器...
docker compose down 2>nul

echo.
echo [2/2] 构建并启动服务...
docker compose up --build -d

echo.
echo ============================================
echo   启动完成！访问地址：
echo   API:      http://localhost:8000
echo   API文档:  http://localhost:8000/docs
echo   Health:   http://localhost:8000/health
echo ============================================
echo.
echo   查看日志: docker compose logs -f api
echo   停止服务: docker compose down
echo.
pause
