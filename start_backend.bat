@echo off
echo 启动 FastAPI 后端服务...
echo.

cd backend

echo 检查 Python 环境...
python --version
if %errorlevel% neq 0 (
    echo 错误: 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo.
echo 检查依赖包...
pip list | findstr fastapi >nul
if %errorlevel% neq 0 (
    echo 安装依赖包...
    pip install -r requirements.txt
)

echo.
echo 检查 Redis 服务...
redis-cli ping >nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: Redis 服务未运行，请先启动 Redis
    echo 下载地址: https://github.com/microsoftarchive/redis/releases
    echo.
    echo 按任意键继续（将使用内存存储，重启后数据丢失）...
    pause
)

echo.
echo 启动 FastAPI 服务器...
echo 服务地址: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo.
echo 按 Ctrl+C 停止服务
echo.

python start.py

pause
