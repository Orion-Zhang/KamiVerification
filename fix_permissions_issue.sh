#!/bin/bash

# CardVerification 权限问题修复脚本
# 解决 collectstatic 权限错误

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 停止现有容器
stop_containers() {
    log_info "停止现有容器..."
    docker-compose -f docker-compose.1panel.yml down || true
    log_success "容器已停止"
}

# 修复本地目录权限
fix_local_permissions() {
    log_info "修复本地目录权限..."
    
    # 创建必要目录
    mkdir -p staticfiles media backups
    
    # 设置目录权限为777，确保容器内用户可以写入
    chmod 777 staticfiles media backups
    
    # 如果目录中有文件，也修复权限
    if [[ -d "staticfiles" && "$(ls -A staticfiles)" ]]; then
        chmod -R 755 staticfiles/*
    fi
    
    if [[ -d "media" && "$(ls -A media)" ]]; then
        chmod -R 755 media/*
    fi
    
    log_success "本地目录权限修复完成"
}

# 创建新的Dockerfile解决权限问题
create_fixed_dockerfile() {
    log_info "创建修复权限的Dockerfile..."
    
    cat > Dockerfile.1panel.fixed << 'EOF'
# 适配1Panel部署的Dockerfile - 修复权限问题
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=CardVerification.settings \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    gettext \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 复制并安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录并设置权限（以root用户运行，避免权限问题）
RUN mkdir -p staticfiles media backups \
    && chmod -R 777 /app

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health/ || exit 1

# 启动命令 - 以root用户运行避免权限问题
CMD ["gunicorn", "CardVerification.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", \
     "--worker-class", "sync", \
     "--worker-connections", "1000", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "100", \
     "--timeout", "30", \
     "--keep-alive", "2", \
     "--preload", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info"]
EOF
    
    log_success "修复权限的Dockerfile已创建"
}

# 更新docker-compose配置使用新的Dockerfile
update_docker_compose() {
    log_info "更新Docker Compose配置..."
    
    # 备份原文件
    cp docker-compose.1panel.yml docker-compose.1panel.yml.backup
    
    # 更新Dockerfile路径
    sed -i 's/dockerfile: Dockerfile.1panel/dockerfile: Dockerfile.1panel.fixed/' docker-compose.1panel.yml
    
    log_success "Docker Compose配置已更新"
}

# 重新构建镜像
rebuild_image() {
    log_info "重新构建Docker镜像..."
    
    # 清理旧镜像
    docker-compose -f docker-compose.1panel.yml build --no-cache web
    
    if [[ $? -eq 0 ]]; then
        log_success "镜像构建完成"
    else
        log_error "镜像构建失败"
        return 1
    fi
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    docker-compose -f docker-compose.1panel.yml up -d
    
    if [[ $? -eq 0 ]]; then
        log_success "服务启动完成"
    else
        log_error "服务启动失败"
        return 1
    fi
}

# 等待服务就绪并收集静态文件
collect_static_in_container() {
    log_info "等待服务就绪..."
    sleep 15
    
    log_info "在容器中收集静态文件..."
    
    # 在容器中运行collectstatic
    if docker-compose -f docker-compose.1panel.yml exec -T web python manage.py collectstatic --noinput --clear; then
        log_success "静态文件收集完成"
    else
        log_warning "静态文件收集失败，尝试手动修复权限..."
        
        # 在容器中修复权限
        docker-compose -f docker-compose.1panel.yml exec -T web chmod -R 777 /app/staticfiles
        
        # 再次尝试收集
        if docker-compose -f docker-compose.1panel.yml exec -T web python manage.py collectstatic --noinput; then
            log_success "静态文件收集完成（第二次尝试）"
        else
            log_error "静态文件收集仍然失败"
            return 1
        fi
    fi
}

# 验证修复结果
verify_fix() {
    log_info "验证修复结果..."
    
    # 检查容器状态
    if docker-compose -f docker-compose.1panel.yml ps | grep -q "Up"; then
        log_success "✅ 容器运行正常"
    else
        log_error "❌ 容器状态异常"
        return 1
    fi
    
    # 检查静态文件
    if [[ -f "staticfiles/css/custom.css" ]]; then
        log_success "✅ 深色主题CSS文件存在"
    else
        log_warning "⚠️ 深色主题CSS文件不存在"
    fi
    
    # 检查应用响应
    sleep 5
    if curl -f http://127.0.0.1:8000/ >/dev/null 2>&1; then
        log_success "✅ 应用响应正常"
    else
        log_warning "⚠️ 应用可能还在启动中"
    fi
}

# 显示后续步骤
show_next_steps() {
    log_info "修复完成！后续步骤："
    echo ""
    echo "1. 清理浏览器缓存并强制刷新页面"
    echo "2. 检查1Panel反向代理配置是否包含静态文件路径"
    echo "3. 如果主题仍然是白色，运行: ./manage_1panel.sh fix-theme"
    echo ""
    echo "查看服务状态: ./manage_1panel.sh status"
    echo "查看日志: ./manage_1panel.sh logs"
}

# 恢复原配置（如果需要）
restore_config() {
    log_warning "恢复原始配置..."
    
    if [[ -f "docker-compose.1panel.yml.backup" ]]; then
        mv docker-compose.1panel.yml.backup docker-compose.1panel.yml
        log_success "配置已恢复"
    fi
    
    if [[ -f "Dockerfile.1panel.fixed" ]]; then
        rm Dockerfile.1panel.fixed
        log_success "临时文件已清理"
    fi
}

# 显示帮助信息
show_help() {
    echo "CardVerification 权限问题修复脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --restore    恢复原始配置"
    echo "  --help       显示此帮助信息"
    echo ""
    echo "此脚本将："
    echo "1. 停止现有容器"
    echo "2. 修复本地目录权限"
    echo "3. 创建修复权限的Dockerfile"
    echo "4. 重新构建镜像"
    echo "5. 启动服务并收集静态文件"
}

# 主函数
main() {
    echo "🔧 CardVerification 权限问题修复工具"
    echo "====================================="
    echo ""
    
    # 解析命令行参数
    case "${1:-}" in
        --restore)
            restore_config
            exit 0
            ;;
        --help)
            show_help
            exit 0
            ;;
    esac
    
    # 执行修复步骤
    stop_containers
    fix_local_permissions
    create_fixed_dockerfile
    update_docker_compose
    rebuild_image
    start_services
    collect_static_in_container
    verify_fix
    show_next_steps
    
    echo ""
    log_success "🎉 权限问题修复完成！"
}

# 运行主函数
main "$@"
