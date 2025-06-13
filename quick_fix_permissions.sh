#!/bin/bash

# 快速修复权限问题脚本

set -e

echo "🔧 快速修复权限问题..."

# 停止容器
echo "停止容器..."
docker-compose -f docker-compose.1panel.yml down || true

# 修复本地目录权限
echo "修复本地目录权限..."
mkdir -p staticfiles media backups
chmod 777 staticfiles media backups

# 清理旧镜像
echo "清理旧镜像..."
docker-compose -f docker-compose.1panel.yml build --no-cache web

# 启动服务
echo "启动服务..."
docker-compose -f docker-compose.1panel.yml up -d

# 等待服务启动
echo "等待服务启动..."
sleep 15

# 在容器中修复权限并收集静态文件
echo "在容器中修复权限..."
docker-compose -f docker-compose.1panel.yml exec -T web chmod -R 777 /app/staticfiles || true

echo "收集静态文件..."
docker-compose -f docker-compose.1panel.yml exec -T web python manage.py collectstatic --noinput --clear

echo "✅ 修复完成！"
echo ""
echo "请："
echo "1. 清理浏览器缓存 (Ctrl+Shift+Delete)"
echo "2. 强制刷新页面 (Ctrl+F5)"
echo ""
echo "检查状态: docker-compose -f docker-compose.1panel.yml ps"
