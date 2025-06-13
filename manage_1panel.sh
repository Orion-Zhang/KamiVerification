#!/bin/bash

# CardVerification 1Panel 环境管理脚本
# 专为1Panel + OpenResty环境设计

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

# 显示帮助信息
show_help() {
    echo "CardVerification 1Panel 环境管理脚本"
    echo ""
    echo "使用方法: ./manage_1panel.sh [command]"
    echo ""
    echo "可用命令:"
    echo "  status      - 查看容器状态"
    echo "  logs        - 查看应用日志"
    echo "  restart     - 重启所有容器"
    echo "  stop        - 停止所有容器"
    echo "  start       - 启动所有容器"
    echo "  backup      - 备份数据库"
    echo "  restore     - 恢复数据库"
    echo "  update      - 更新应用"
    echo "  shell       - 进入应用容器"
    echo "  dbshell     - 进入数据库"
    echo "  migrate     - 运行数据库迁移"
    echo "  collectstatic - 收集静态文件"
    echo "  createsuperuser - 创建超级用户"
    echo "  cleanup     - 清理系统"
    echo "  monitor     - 监控容器资源"
    echo "  1panel-info - 显示1Panel配置信息"
    echo "  health      - 健康检查"
    echo "  help        - 显示此帮助信息"
}

# 检查容器状态
check_status() {
    log_info "检查容器状态..."
    docker-compose -f docker-compose.1panel.yml ps
    echo
    log_info "容器资源使用情况:"
    docker stats --no-stream $(docker-compose -f docker-compose.1panel.yml ps -q) 2>/dev/null || true
}

# 查看日志
view_logs() {
    log_info "查看容器日志..."
    echo "选择要查看的日志:"
    echo "1) Web应用日志"
    echo "2) 数据库日志"
    echo "3) Redis日志"
    echo "4) 所有容器日志"

    read -p "请选择 (1-4): " choice

    case $choice in
        1)
            docker-compose -f docker-compose.1panel.yml logs -f --tail=100 web
            ;;
        2)
            docker-compose -f docker-compose.1panel.yml logs -f --tail=50 db
            ;;
        3)
            docker-compose -f docker-compose.1panel.yml logs -f --tail=50 redis
            ;;
        4)
            docker-compose -f docker-compose.1panel.yml logs -f --tail=100
            ;;
        *)
            log_error "无效选择"
            ;;
    esac
}

# 重启服务
restart_services() {
    log_info "重启所有容器..."
    docker-compose -f docker-compose.1panel.yml restart
    log_success "容器重启完成"
}

# 停止服务
stop_services() {
    log_warning "停止所有容器..."
    docker-compose -f docker-compose.1panel.yml down
    log_success "容器已停止"
}

# 启动服务
start_services() {
    log_info "启动所有容器..."
    docker-compose -f docker-compose.1panel.yml up -d
    log_success "容器已启动"
}

# 备份数据库
backup_database() {
    log_info "备份数据库..."
    
    # 创建备份目录
    mkdir -p backups
    
    # 生成备份文件名
    BACKUP_FILE="backups/cardverification_$(date +%Y%m%d_%H%M%S).sql"
    
    # 执行备份
    docker-compose -f docker-compose.1panel.yml exec -T db pg_dump -U ${POSTGRES_USER:-cardverification} ${POSTGRES_DB:-cardverification} > $BACKUP_FILE
    
    # 压缩备份文件
    gzip $BACKUP_FILE
    
    log_success "数据库备份完成: ${BACKUP_FILE}.gz"
}

# 更新应用
update_application() {
    log_info "更新应用..."
    
    # 备份数据
    backup_database
    
    # 拉取最新代码
    git pull origin main
    
    # 重新构建镜像
    docker-compose -f docker-compose.1panel.yml build --no-cache web
    
    # 重启服务
    docker-compose -f docker-compose.1panel.yml up -d
    
    # 运行迁移
    docker-compose -f docker-compose.1panel.yml exec web python manage.py migrate
    
    # 收集静态文件
    docker-compose -f docker-compose.1panel.yml exec web python manage.py collectstatic --noinput
    
    log_success "应用更新完成"
}

# 进入应用容器
enter_shell() {
    log_info "进入应用容器..."
    docker-compose -f docker-compose.1panel.yml exec web bash
}

# 进入数据库
enter_dbshell() {
    log_info "进入数据库..."
    docker-compose -f docker-compose.1panel.yml exec web python manage.py dbshell
}

# 运行迁移
run_migrations() {
    log_info "运行数据库迁移..."
    docker-compose -f docker-compose.1panel.yml exec web python manage.py migrate
    log_success "迁移完成"
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
    docker-compose -f docker-compose.1panel.yml exec web python manage.py createsuperuser
}

# 清理系统
cleanup_system() {
    log_info "清理系统..."
    
    # 清理 Docker 镜像
    docker system prune -f
    
    # 清理旧的备份文件 (保留最近30天)
    find backups -name "*.sql.gz" -mtime +30 -delete 2>/dev/null || true
    
    # 清理大日志文件
    find logs -name "*.log" -size +100M -exec truncate -s 0 {} \; 2>/dev/null || true
    
    log_success "系统清理完成"
}

# 监控容器资源
monitor_system() {
    log_info "容器资源监控..."
    
    echo "=== 容器状态 ==="
    docker-compose -f docker-compose.1panel.yml ps
    
    echo ""
    echo "=== 容器资源使用 ==="
    docker stats --no-stream $(docker-compose -f docker-compose.1panel.yml ps -q) 2>/dev/null || true
    
    echo ""
    echo "=== 磁盘使用情况 ==="
    df -h
    
    echo ""
    echo "=== 内存使用情况 ==="
    free -h
}

# 显示1Panel配置信息
show_1panel_info() {
    log_info "1Panel配置信息"
    echo
    echo "=== 反向代理配置 ==="
    echo "域名: kami.killua.tech"
    echo "代理目标: http://127.0.0.1:8000"
    echo "SSL: 启用"
    echo
    echo "=== 静态文件代理 ==="
    echo "路径: /static/"
    echo "目标: http://127.0.0.1:8000/static/"
    echo
    echo "路径: /media/"
    echo "目标: http://127.0.0.1:8000/media/"
    echo
    echo "=== 容器信息 ==="
    echo "应用端口: 127.0.0.1:8000"
    echo "数据库: PostgreSQL (内部网络)"
    echo "缓存: Redis (内部网络)"
    echo
    echo "=== 访问地址 ==="
    echo "主页: https://kami.killua.tech"
    echo "管理后台: https://kami.killua.tech/admin/"
    echo "API文档: https://kami.killua.tech/swagger/"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 检查容器状态
    if docker-compose -f docker-compose.1panel.yml ps | grep -q "Up"; then
        log_success "✅ 容器运行正常"
    else
        log_error "❌ 容器状态异常"
        return 1
    fi
    
    # 检查应用响应
    if curl -f http://127.0.0.1:8000/api/v1/health/ >/dev/null 2>&1; then
        log_success "✅ 应用响应正常"
    else
        log_error "❌ 应用无响应"
        return 1
    fi
    
    # 检查数据库连接
    if docker-compose -f docker-compose.1panel.yml exec -T db pg_isready -U ${POSTGRES_USER:-cardverification} >/dev/null 2>&1; then
        log_success "✅ 数据库连接正常"
    else
        log_error "❌ 数据库连接失败"
        return 1
    fi
    
    # 检查Redis连接
    if docker-compose -f docker-compose.1panel.yml exec -T redis redis-cli ping >/dev/null 2>&1; then
        log_success "✅ Redis连接正常"
    else
        log_error "❌ Redis连接失败"
        return 1
    fi
    
    log_success "🎉 所有健康检查通过"
}

# 主函数
main() {
    case "${1:-help}" in
        status)
            check_status
            ;;
        logs)
            view_logs
            ;;
        restart)
            restart_services
            ;;
        stop)
            stop_services
            ;;
        start)
            start_services
            ;;
        backup)
            backup_database
            ;;
        update)
            update_application
            ;;
        shell)
            enter_shell
            ;;
        dbshell)
            enter_dbshell
            ;;
        migrate)
            run_migrations
            ;;
        collectstatic)
            collect_static
            ;;
        createsuperuser)
            create_superuser
            ;;
        cleanup)
            cleanup_system
            ;;
        monitor)
            monitor_system
            ;;
        1panel-info)
            show_1panel_info
            ;;
        health)
            health_check
            ;;
        help|*)
            show_help
            ;;
    esac
}

# 执行主函数
main "$@"
