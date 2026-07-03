# ============================================================
# 一键启动后端服务
# 用法: .\start-backend.ps1 [-SkipNestJS] [-SkipFastAPI] [-SkipDocker]
# ============================================================
param(
    [switch]$SkipNestJS,
    [switch]$SkipFastAPI,
    [switch]$SkipDocker
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  一键启动后端服务" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ---- 检查 Node 版本 ----
if (-not $SkipNestJS) {
    $nodeVersion = & node -v 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] 未找到 Node.js，请先安装 Node >= 22" -ForegroundColor Red
        Write-Host "        下载: https://nodejs.org" -ForegroundColor Yellow
        exit 1
    }
    $major = [int]($nodeVersion -replace 'v','' -replace '\..*')
    if ($major -lt 22) {
        Write-Host "[WARN] Node 版本为 $nodeVersion，建议 >= 22" -ForegroundColor Yellow
    }
    Write-Host "[OK] Node $nodeVersion" -ForegroundColor Green
}

# ---- 检查 Python venv ----
if (-not $SkipFastAPI) {
    $venvActivate = Join-Path $Root "fastapi-backend\.venv\Scripts\Activate.ps1"
    if (-not (Test-Path $venvActivate)) {
        Write-Host "[ERROR] FastAPI venv 不存在: $venvActivate" -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] FastAPI venv 就绪" -ForegroundColor Green
}

# ---- Docker 依赖服务 ----
if (-not $SkipDocker) {
    $dockerRunning = & docker info 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[WARN] Docker 未运行，跳过容器启动 (Postgres/Redis/Ollama)" -ForegroundColor Yellow
        Write-Host "       请手动启动 Docker Desktop 后重试，或确保这些服务已运行" -ForegroundColor Yellow
    } else {
        Write-Host "[INFO] 启动 Docker 依赖服务 (Postgres + Redis)..." -ForegroundColor Gray
        Push-Location $Root
        docker compose up -d postgres redis 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Docker 依赖服务已启动" -ForegroundColor Green
        } else {
            Write-Host "[WARN] Docker compose 启动失败，请检查 docker-compose.yml" -ForegroundColor Yellow
        }
        Pop-Location
    }
}

# ---- 启动 FastAPI 后端 ----
if (-not $SkipFastAPI) {
    Write-Host ""
    Write-Host "----------------------------------------" -ForegroundColor Cyan
    Write-Host "  启动 FastAPI 后端 (端口 8000)" -ForegroundColor Cyan
    Write-Host "----------------------------------------" -ForegroundColor Cyan

    $tmpScript = Join-Path $env:TEMP "start-fastapi.ps1"
    @"
Set-Location "$Root\fastapi-backend"
. "$venvActivate"
Write-Host "[INFO] FastAPI 启动中 (uvicorn --reload)..." -ForegroundColor Gray
Write-Host "     Swagger: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host "     Health:  http://localhost:8000/health" -ForegroundColor Gray
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"@ | Set-Content -Path $tmpScript -Encoding UTF8

    Start-Process powershell -ArgumentList "-NoExit", "-File", $tmpScript
    Write-Host "[OK] FastAPI 已在新窗口启动 (端口 8000)" -ForegroundColor Green
}

# ---- 启动 NestJS 服务端 ----
if (-not $SkipNestJS) {
    Write-Host ""
    Write-Host "----------------------------------------" -ForegroundColor Cyan
    Write-Host "  启动 NestJS 服务端 (端口 3000)" -ForegroundColor Cyan
    Write-Host "----------------------------------------" -ForegroundColor Cyan

    # 检查 node_modules
    if (-not (Test-Path (Join-Path $Root "node_modules"))) {
        Write-Host "[INFO] 安装依赖 (npm install)..." -ForegroundColor Gray
        Push-Location $Root
        npm install 2>&1 | Out-Null
        Pop-Location
        Write-Host "[OK] 依赖安装完成" -ForegroundColor Green
    }

    $tmpScript = Join-Path $env:TEMP "start-nestjs.ps1"
    @"
Set-Location "$Root"
Write-Host "[INFO] NestJS 启动中 (nest --watch)..." -ForegroundColor Gray
Write-Host "     http://localhost:3000" -ForegroundColor Gray
`$env:NODE_ENV = "development"
npx nest start --watch
"@ | Set-Content -Path $tmpScript -Encoding UTF8

    Start-Process powershell -ArgumentList "-NoExit", "-File", $tmpScript
    Write-Host "[OK] NestJS 已在新窗口启动 (端口 3000)" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  后端服务启动完毕！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  FastAPI : http://localhost:8000/docs" -ForegroundColor White
Write-Host "  NestJS  : http://localhost:3000" -ForegroundColor White
Write-Host ""

Write-Host "按任意键关闭此窗口 (不影响后端运行)..." -ForegroundColor DarkGray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
