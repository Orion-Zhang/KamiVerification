#!/bin/bash

# CardVerification 1Panel 部署脚本
# 专为1Panel + OpenResty环境优化

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 检查1Panel环境
check_1panel_environment() {
    log_info "检查1Panel部署环境..."
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装"
        exit 1
    fi
    
    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装"
        exit 1
    fi
    
    # 检查环境文件
    if [[ ! -f ".env" ]]; then
        if [[ -f ".env.1panel.example" ]]; then
            log_warning "环境配置文件 .env 不存在，正在复制模板..."
            cp .env.1panel.example .env
            log_warning "请编辑 .env 文件配置相应参数后重新运行部署脚本"
            exit 1
        else
            log_error "环境配置文件不存在"
            exit 1
        fi
    fi
    
    log_success "1Panel环境检查通过"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."

    # 创建数据目录（移除logs目录）
    mkdir -p media staticfiles backups

    # 设置权限 (适配1Panel容器管理)
    chmod 755 media staticfiles backups

    log_success "目录创建完成"
}

# 构建和启动服务
deploy_services() {
    log_info "使用1Panel优化配置部署服务..."
    
    # 停止现有服务
    docker-compose -f docker-compose.1panel.yml down 2>/dev/null || true
    
    # 构建镜像
    log_info "构建应用镜像..."
    docker-compose -f docker-compose.1panel.yml build --no-cache
    
    # 启动服务
    log_info "启动服务..."
    docker-compose -f docker-compose.1panel.yml up -d
    
    log_success "服务启动完成"
}

# 等待服务就绪
wait_for_services() {
    log_info "等待服务就绪..."
    
    # 等待数据库
    log_info "等待数据库服务..."
    for i in {1..30}; do
        if docker-compose -f docker-compose.1panel.yml exec db pg_isready -U ${POSTGRES_USER:-cardverification} >/dev/null 2>&1; then
            break
        fi
        sleep 2
    done
    
    # 等待Redis
    log_info "等待Redis服务..."
    for i in {1..15}; do
        if docker-compose -f docker-compose.1panel.yml exec redis redis-cli ping >/dev/null 2>&1; then
            break
        fi
        sleep 2
    done
    
    # 等待应用
    log_info "等待应用服务..."
    sleep 10
    
    log_success "服务就绪"
}

# 运行数据库迁移
run_migrations() {
    log_info "运行数据库迁移..."
    
    docker-compose -f docker-compose.1panel.yml exec web python manage.py migrate
    
    log_success "数据库迁移完成"
}

# 收集静态文件
collect_static() {
    log_info "收集静态文件..."
    
    docker-compose -f docker-compose.1panel.yml exec web python manage.py collectstatic --noinput
    
    log_success "静态文件收集完成"
}

# 创建超级用户
create_superuser() {
    log_info "创建超级用户..."
    log_warning "请按提示输入超级用户信息"
    docker-compose -f docker-compose.1panel.yml exec web python manage.py createsuperuser
}

# 显示1Panel部署信息
show_deployment_info() {
    log_success "1Panel部署完成！"
    echo
    log_info "部署信息:"
    echo "  - 容器应用端口: 127.0.0.1:8000"
    echo "  - 数据库容器: cardverification_db"
    echo "  - Redis容器: cardverification_redis"
    echo "  - 应用容器: cardverification_web"
    echo
    log_info "1Panel配置建议:"
    echo "  - 在1Panel中创建网站: kami.killua.tech"
    echo "  - 反向代理目标: http://127.0.0.1:8000"
    echo "  - 启用SSL证书"
    echo "  - 配置静态文件代理:"
    echo "    * /static/ -> http://127.0.0.1:8000/static/"
    echo "    * /media/ -> http://127.0.0.1:8000/media/"
    echo
    log_info "访问地址:"
    echo "  - 应用地址: https://kami.killua.tech"
    echo "  - 管理后台: https://kami.killua.tech/admin/"
    echo "  - API文档: https://kami.killua.tech/swagger/"
    echo
    log_info "容器管理命令:"
    echo "  - 查看状态: docker-compose -f docker-compose.1panel.yml ps"
    echo "  - 查看日志: docker-compose -f docker-compose.1panel.yml logs -f"
    echo "  - 重启服务: docker-compose -f docker-compose.1panel.yml restart"
    echo "  - 进入容器: docker-compose -f docker-compose.1panel.yml exec web bash"
}

# 检查部署状态
check_deployment() {
    log_info "检查部署状态..."
    
    # 检查容器状态
    if docker-compose -f docker-compose.1panel.yml ps | grep -q "Up"; then
        log_success "容器运行正常"
    else
        log_error "容器状态异常"
        docker-compose -f docker-compose.1panel.yml ps
        return 1
    fi
    
    # 检查应用健康状态
    if curl -f http://127.0.0.1:8000/api/v1/health/ >/dev/null 2>&1; then
        log_success "应用健康检查通过"
    else
        log_warning "应用健康检查失败，请检查日志"
    fi
    
    return 0
}

# 主函数
main() {
    log_info "开始1Panel环境部署 CardVerification 项目"
    
    check_1panel_environment
    create_directories
    deploy_services
    wait_for_services
    run_migrations
    collect_static
    
    # 询问是否创建超级用户
    read -p "是否创建超级用户？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_superuser
    fi
    
    check_deployment
    show_deployment_info
}

# 执行主函数
main "$@"
