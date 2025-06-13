#!/bin/bash

# ===== Docker 容器启动脚本 =====
# 用于初始化Django应用和数据库

set -e

# 颜色输出函数
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
    
    # 从DATABASE_URL中提取数据库连接信息
    if [ -n "$DATABASE_URL" ]; then
        # 解析PostgreSQL URL: postgresql://user:password@host:port/dbname
        DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
        DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    else
        DB_HOST=${DB_HOST:-db}
        DB_PORT=${DB_PORT:-5432}
    fi
    
    log_info "检查数据库连接: $DB_HOST:$DB_PORT"
    
    until nc -z $DB_HOST $DB_PORT; do
        log_warning "数据库尚未就绪，等待中..."
        sleep 2
    done
    
    log_success "数据库连接成功！"
}

# 等待Redis服务启动
wait_for_redis() {
    log_info "等待Redis服务启动..."
    
    REDIS_HOST=${REDIS_HOST:-redis}
    REDIS_PORT=${REDIS_PORT:-6379}
    
    log_info "检查Redis连接: $REDIS_HOST:$REDIS_PORT"
    
    until nc -z $REDIS_HOST $REDIS_PORT; do
        log_warning "Redis尚未就绪，等待中..."
        sleep 2
    done
    
    log_success "Redis连接成功！"
}

# 运行数据库迁移
run_migrations() {
    log_info "开始数据库迁移..."

    # 设置超时时间
    timeout 300 bash -c '
        # 检查是否需要创建迁移文件
        python manage.py makemigrations --check --dry-run > /dev/null 2>&1
        if [ $? -ne 0 ]; then
            echo "检测到模型变更，创建迁移文件..."
            python manage.py makemigrations
        fi

        # 运行迁移
        echo "执行数据库迁移..."
        python manage.py migrate --noinput
    '

    if [ $? -eq 0 ]; then
        log_success "数据库迁移完成！"
    else
        log_error "数据库迁移失败或超时！"
        # 不要立即退出，尝试继续启动
        log_warning "跳过迁移，继续启动服务..."
    fi
}

# 收集静态文件
collect_static() {
    log_info "收集静态文件..."
    
    python manage.py collectstatic --noinput --clear
    
    if [ $? -eq 0 ]; then
        log_success "静态文件收集完成！"
    else
        log_error "静态文件收集失败！"
        exit 1
    fi
}

# 创建超级用户
create_superuser() {
    log_info "检查超级用户..."
    
    if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
        python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('超级用户创建成功！')
else:
    print('超级用户已存在，跳过创建。')
EOF
        log_success "超级用户检查完成！"
    else
        log_warning "未设置超级用户环境变量，跳过创建。"
    fi
}

# 加载初始数据
load_fixtures() {
    log_info "检查是否需要加载初始数据..."
    
    # 检查是否存在fixtures文件
    if [ -d "fixtures" ] && [ "$(ls -A fixtures)" ]; then
        log_info "加载初始数据..."
        for fixture in fixtures/*.json; do
            if [ -f "$fixture" ]; then
                log_info "加载: $fixture"
                python manage.py loaddata "$fixture"
            fi
        done
        log_success "初始数据加载完成！"
    else
        log_info "未找到初始数据文件，跳过加载。"
    fi
}

# 健康检查
health_check() {
    log_info "执行应用健康检查..."
    
    python -c "
import django
django.setup()
from django.db import connection
from django.core.cache import cache

# 检查数据库连接
try:
    connection.ensure_connection()
    print('数据库连接正常')
except Exception as e:
    print(f'数据库连接失败: {e}')
    exit(1)

# 检查缓存连接
try:
    cache.set('health_check', 'ok', 30)
    if cache.get('health_check') == 'ok':
        print('缓存连接正常')
    else:
        print('缓存连接异常')
except Exception as e:
    print(f'缓存连接失败: {e}')
"
    
    if [ $? -eq 0 ]; then
        log_success "应用健康检查通过！"
    else
        log_error "应用健康检查失败！"
        exit 1
    fi
}

# 主函数
main() {
    log_info "=== 卡片验证系统容器启动 ==="
    log_info "Django版本: $(python -c 'import django; print(django.get_version())')"
    log_info "Python版本: $(python --version)"
    
    # 等待依赖服务
    wait_for_db
    wait_for_redis
    
    # 初始化应用
    run_migrations
    collect_static
    create_superuser
    load_fixtures
    
    # 健康检查
    health_check
    
    log_success "=== 容器初始化完成，启动应用服务 ==="
    
    # 执行传入的命令
    exec "$@"
}

# 如果脚本被直接执行，运行主函数
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
