# 使用官方 Python 3.11 镜像作为基础镜像
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    TZ=Asia/Shanghai

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建非root用户
RUN groupadd -r django && useradd -r -g django django

# 复制requirements文件并安装Python依赖
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . /app/

# 创建必要的目录
RUN mkdir -p /app/static /app/media /app/logs && \
    chown -R django:django /app

# 复制并设置启动脚本权限
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# 切换到非root用户
USER django

# 暴露端口
EXPOSE 8000

# 设置启动命令
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "CardVerification.wsgi:application"]
