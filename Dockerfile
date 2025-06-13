# ===== 多阶段构建 Dockerfile =====
# 第一阶段：构建阶段
FROM python:3.11-slim as builder

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 创建虚拟环境
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 复制并安装Python依赖
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ===== 第二阶段：运行阶段 =====
FROM python:3.11-slim as runner

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=CardVerification.settings

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    libpq5 \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 创建应用用户
RUN groupadd -r django && useradd -r -g django django

# 从构建阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 创建必要的目录并设置权限
RUN mkdir -p /app/staticfiles /app/media /app/logs && \
    chown -R django:django /app

# 复制启动脚本
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh && \
    chown django:django /usr/local/bin/docker-entrypoint.sh

# 切换到非root用户
USER django

# 收集静态文件
RUN python manage.py collectstatic --noinput --clear

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health/', timeout=10)" || exit 1

# 设置入口点
ENTRYPOINT ["docker-entrypoint.sh"]

# 默认命令
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "--keep-alive", "2", "--max-requests", "1000", "--max-requests-jitter", "100", "CardVerification.wsgi:application"]
