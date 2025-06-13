#!/bin/bash

# CardVerification 生产环境管理脚本
# 使用方法: ./manage_prod.sh [command]

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
    echo "CardVerification 生产环境管理脚本"
    echo ""
    echo "使用方法: ./manage_prod.sh [command]"
    echo ""
    echo "可用命令:"
    echo "  status      - 查看服务状态"
    echo "  logs        - 查看应用日志"
    echo "  restart     - 重启所有服务"
    echo "  stop        - 停止所有服务"
    echo "  start       - 启动所有服务"
    echo "  backup      - 备份数据库"
    echo "  restore     - 恢复数据库"
    echo "  update      - 更新应用"
    echo "  shell       - 进入应用容器"
    echo "  dbshell     - 进入数据库"
    echo "  migrate     - 运行数据库迁移"
    echo "  collectstatic - 收集静态文件"
    echo "  createsuperuser - 创建超级用户"
    echo "  cleanup     - 清理系统"
    echo "  monitor     - 监控系统资源"
    echo "  help        - 显示此帮助信息"
}

# 检查服务状态
check_status() {
    log_info "检查服务状态..."
    docker-compose -f docker-compose.prod.yml ps
}

# 查看日志
view_logs() {
    log_info "查看应用日志..."
    docker-compose -f docker-compose.prod.yml logs -f --tail=100
}

# 重启服务
restart_services() {
    log_info "重启所有服务..."
    docker-compose -f docker-compose.prod.yml restart
    log_success "服务重启完成"
}

# 停止服务
stop_services() {
    log_warning "停止所有服务..."
    docker-compose -f docker-compose.prod.yml down
    log_success "服务已停止"
}

# 启动服务
start_services() {
    log_info "启动所有服务..."
    docker-compose -f docker-compose.prod.yml up -d
    log_success "服务已启动"
}

# 备份数据库
backup_database() {
    log_info "备份数据库..."
    
    # 创建备份目录
    mkdir -p backups
    
    # 生成备份文件名
    BACKUP_FILE="backups/cardverification_$(date +%Y%m%d_%H%M%S).sql"
    
    # 执行备份
    docker-compose -f docker-compose.prod.yml exec db pg_dump -U $POSTGRES_USER $POSTGRES_DB > $BACKUP_FILE
    
    # 压缩备份文件
    gzip $BACKUP_FILE
    
    log_success "数据库备份完成: ${BACKUP_FILE}.gz"
}

# 恢复数据库
restore_database() {
    log_warning "恢复数据库..."
    
    # 列出可用的备份文件
    echo "可用的备份文件:"
    ls -la backups/*.sql.gz 2>/dev/null || {
        log_error "没有找到备份文件"
        exit 1
    }
    
    echo ""
    read -p "请输入要恢复的备份文件名: " BACKUP_FILE
    
    if [[ ! -f "$BACKUP_FILE" ]]; then
        log_error "备份文件不存在: $BACKUP_FILE"
        exit 1
    fi
    
    # 确认操作
    read -p "确认要恢复数据库吗？这将覆盖现有数据 (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "操作已取消"
        exit 0
    fi
    
    # 解压并恢复
    gunzip -c $BACKUP_FILE | docker-compose -f docker-compose.prod.yml exec -T db psql -U $POSTGRES_USER -d $POSTGRES_DB
    
    log_success "数据库恢复完成"
}

# 更新应用
update_application() {
    log_info "更新应用..."
    
    # 拉取最新代码
    git pull origin main
    
    # 重新构建镜像
    docker-compose -f docker-compose.prod.yml build --no-cache web
    
    # 重启服务
    docker-compose -f docker-compose.prod.yml up -d
    
    # 运行迁移
    docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
    
    # 收集静态文件
    docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
    
    log_success "应用更新完成"
}

# 进入应用容器
enter_shell() {
    log_info "进入应用容器..."
    docker-compose -f docker-compose.prod.yml exec web bash
}

# 进入数据库
enter_dbshell() {
    log_info "进入数据库..."
    docker-compose -f docker-compose.prod.yml exec web python manage.py dbshell
}

# 运行迁移
run_migrations() {
    log_info "运行数据库迁移..."
    docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
    log_success "迁移完成"
}

# 收集静态文件
collect_static() {
    log_info "收集静态文件..."
    docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
    log_success "静态文件收集完成"
}

# 创建超级用户
create_superuser() {
    log_info "创建超级用户..."
    docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
}

# 清理系统
cleanup_system() {
    log_info "清理系统..."
    
    # 清理 Docker 镜像
    docker system prune -f
    
    # 清理旧的备份文件 (保留最近30天)
    find backups -name "*.sql.gz" -mtime +30 -delete 2>/dev/null || true
    
    # 清理日志文件
    find logs -name "*.log" -size +100M -exec truncate -s 0 {} \; 2>/dev/null || true
    
    log_success "系统清理完成"
}

# 监控系统资源
monitor_system() {
    log_info "系统资源监控..."
    
    echo "=== Docker 容器状态 ==="
    docker-compose -f docker-compose.prod.yml ps
    
    echo ""
    echo "=== 系统资源使用 ==="
    docker stats --no-stream
    
    echo ""
    echo "=== 磁盘使用情况 ==="
    df -h
    
    echo ""
    echo "=== 内存使用情况 ==="
    free -h
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
        restore)
            restore_database
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
        help|*)
            show_help
            ;;
    esac
}

# 执行主函数
main "$@"
