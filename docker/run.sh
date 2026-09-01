#!/bin/sh
# 单容器启动脚本：后台启动 FastAPI(uvicorn)，前台运行 nginx
set -e

# 确保数据目录存在
mkdir -p /app/backend/data

# 后台启动 uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
UVICORN_PID=$!
echo "uvicorn started (pid $UVICORN_PID)"

# 用 python 健康检查等待 uvicorn 就绪
for i in $(seq 1 30); do
    if python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=1).status==200 else 1)" >/dev/null 2>&1; then
        echo "uvicorn ready after ${i}s"
        break
    fi
    sleep 1
done

# 前台运行 nginx
echo "starting nginx..."
exec nginx -g "daemon off;"