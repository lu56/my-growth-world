# ===== 阶段1：构建前端静态资源 =====
FROM node:20-alpine AS frontend-build
WORKDIR /app
COPY frontend/package.json ./
COPY frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ===== 阶段2：安装后端 Python 依赖 =====
FROM python:3.12-slim AS backend-deps
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ===== 阶段3：运行镜像（nginx + FastAPI 单容器） =====
FROM python:3.12-slim AS runtime
# 安装 nginx
RUN apt-get update && apt-get install -y --no-install-recommends nginx \
    && rm -rf /var/lib/apt/lists/*

# 复制后端依赖
COPY --from=backend-deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=backend-deps /usr/local/bin /usr/local/bin

# 复制后端代码
WORKDIR /app/backend
COPY backend/app ./app
RUN mkdir -p data

# 复制前端静态资源 + nginx 配置
COPY --from=frontend-build /app/dist /usr/share/nginx/html
# 校验前端产物存在，避免空镜像
RUN test -f /usr/share/nginx/html/index.html \
    && echo "前端产物 OK: $(ls /usr/share/nginx/html | wc -l) 个文件"
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# 移除 Debian 默认站点，避免其抢占 80 端口导致显示 nginx 欢迎页
RUN rm -f /etc/nginx/sites-enabled/default /etc/nginx/sites-available/default \
    && rm -rf /var/www/html/index.nginx-debian.html

# 启动脚本
COPY docker/run.sh /run.sh
RUN chmod +x /run.sh

EXPOSE 80
CMD ["/run.sh"]