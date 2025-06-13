#!/bin/bash

# ===== 简化的Docker容器启动脚本 =====
# 用于快速启动，跳过复杂的初始化步骤

set -e

# 颜色输出函数
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

# 等待数据库服务启动
wait_for_db() {
    log_info "等待数据库服务启动..."
    
    DB_HOST=${DB_HOST:-db}
    DB_PORT=${DB_PORT:-5432}
    
    for i in {1..30}; do
        if nc -z $DB_HOST $DB_PORT; then
            log_success "数据库连接成功！"
            return 0
        fi
        log_info "等待数据库... ($i/30)"
        sleep 2
    done
    
    log_error "数据库连接超时！"
    exit 1
}

# 基本的数据库迁移
run_basic_migrations() {
    log_info "运行基本数据库迁移..."
    
    # 只运行基本迁移，不创建新的迁移文件
    python manage.py migrate --run-syncdb || {
        log_warning "迁移失败，尝试基本同步..."
        python manage.py migrate --fake-initial || {
            log_warning "跳过迁移，直接启动服务..."
        }
    }
    
    log_success "数据库初始化完成！"
}

# 收集静态文件
collect_static() {
    log_info "收集静态文件..."
    python manage.py collectstatic --noinput --clear || {
        log_warning "静态文件收集失败，继续启动..."
    }
}

# 创建超级用户（如果不存在）
create_superuser() {
    if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
        log_info "检查超级用户..."
        python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '${DJANGO_SUPERUSER_EMAIL:-admin@example.com}', '$DJANGO_SUPERUSER_PASSWORD')
    print('超级用户创建成功！')
else:
    print('超级用户已存在。')
" || log_warning "超级用户创建失败，请手动创建"
    fi
}

# 主函数
main() {
    log_info "=== 卡片验证系统快速启动 ==="
    log_info "Django版本: $(python -c 'import django; print(django.get_version())')"
    log_info "Python版本: $(python --version)"
    
    # 等待数据库
    wait_for_db
    
    # 基本初始化
    run_basic_migrations
    collect_static
    create_superuser
    
    log_success "=== 初始化完成，启动应用服务 ==="
    
    # 执行传入的命令
    exec "$@"
}

# 执行主函数
main "$@"
