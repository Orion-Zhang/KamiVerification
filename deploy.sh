#!/bin/bash

# CardVerification 项目部署脚本
# 使用方法: ./deploy.sh [dev|prod]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
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

# 检查参数
ENVIRONMENT=${1:-dev}

if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prod" ]]; then
    log_error "无效的环境参数。使用: ./deploy.sh [dev|prod]"
    exit 1
fi

log_info "开始部署 CardVerification 项目 - 环境: $ENVIRONMENT"

# 检查必要的文件
check_requirements() {
    log_info "检查部署要求..."
    
    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装"
        exit 1
    fi
    
    # 检查 Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装"
        exit 1
    fi
    
    # 检查环境文件
    if [[ "$ENVIRONMENT" == "prod" ]]; then
        if [[ ! -f ".env.production" ]]; then
            log_error "生产环境配置文件 .env.production 不存在"
            log_info "请复制 .env.production.example 为 .env.production 并配置相应参数"
            exit 1
        fi
    fi
    
    log_success "部署要求检查通过"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p logs
    mkdir -p media
    mkdir -p backups
    
    # 设置权限
    chmod 755 logs media backups
    
    log_success "目录创建完成"
}

# 构建和启动服务
deploy_services() {
    log_info "构建和启动服务..."
    
    if [[ "$ENVIRONMENT" == "prod" ]]; then
        # 生产环境部署
        log_info "使用生产环境配置部署..."
        docker-compose -f docker-compose.prod.yml down
        docker-compose -f docker-compose.prod.yml build --no-cache
        docker-compose -f docker-compose.prod.yml up -d
    else
        # 开发环境部署
        log_info "使用开发环境配置部署..."
        docker-compose down
        docker-compose build --no-cache
        docker-compose up -d
    fi
    
    log_success "服务启动完成"
}

# 等待服务就绪
wait_for_services() {
    log_info "等待服务就绪..."
    
    # 等待数据库
    log_info "等待数据库服务..."
    sleep 10
    
    # 等待应用
    log_info "等待应用服务..."
    sleep 5
    
    log_success "服务就绪"
}

# 运行数据库迁移
run_migrations() {
    log_info "运行数据库迁移..."
    
    if [[ "$ENVIRONMENT" == "prod" ]]; then
        docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
    else
        docker-compose exec web python manage.py migrate
    fi
    
    log_success "数据库迁移完成"
}

# 收集静态文件
collect_static() {
    log_info "收集静态文件..."
    
    if [[ "$ENVIRONMENT" == "prod" ]]; then
        docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
    else
        docker-compose exec web python manage.py collectstatic --noinput
    fi
    
    log_success "静态文件收集完成"
}

# 创建超级用户 (仅开发环境)
create_superuser() {
    if [[ "$ENVIRONMENT" == "dev" ]]; then
        log_info "创建超级用户 (开发环境)..."
        log_warning "请按提示输入超级用户信息"
        docker-compose exec web python manage.py createsuperuser
    fi
}

# 显示部署信息
show_deployment_info() {
    log_success "部署完成！"
    echo
    log_info "服务访问地址:"
    
    if [[ "$ENVIRONMENT" == "prod" ]]; then
        echo "  - 应用地址: https://yourdomain.com"
        echo "  - 管理后台: https://yourdomain.com/admin/"
        echo "  - API文档: https://yourdomain.com/swagger/"
    else
        echo "  - 应用地址: http://localhost"
        echo "  - 管理后台: http://localhost/admin/"
        echo "  - API文档: http://localhost/swagger/"
        echo "  - 直接访问: http://localhost:8000"
    fi
    
    echo
    log_info "常用命令:"
    echo "  - 查看日志: docker-compose logs -f"
    echo "  - 停止服务: docker-compose down"
    echo "  - 重启服务: docker-compose restart"
    echo "  - 进入容器: docker-compose exec web bash"
}

# 主函数
main() {
    check_requirements
    create_directories
    deploy_services
    wait_for_services
    run_migrations
    collect_static
    create_superuser
    show_deployment_info
}

# 执行主函数
main
