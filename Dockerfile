# 使用官方 Python 3.11 slim 镜像
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=CardVerification.settings \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 设置工作目录
WORKDIR /app

# 创建应用用户和组
RUN groupadd -r django && useradd -r -g django django

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 复制并安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p logs staticfiles media \
    && chown -R django:django /app

# 切换到应用用户
USER django

# 收集静态文件
RUN python manage.py collectstatic --noinput

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health/ || exit 1

# 启动命令
CMD ["gunicorn", "CardVerification.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--worker-class", "sync", \
     "--worker-connections", "1000", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "100", \
     "--timeout", "30", \
     "--keep-alive", "2", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
