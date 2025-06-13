#!/bin/bash

# 卡片验证系统 Docker 部署脚本
# 作者: Killua
# 版本: 1.0

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

# 检查 Docker 和 Docker Compose
check_docker() {
    log_info "检查 Docker 环境..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    log_success "Docker 环境检查通过"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p backups
    mkdir -p ssl
    mkdir -p logs
    
    log_success "目录创建完成"
}

# 生成环境配置文件
setup_env() {
    if [ ! -f .env ]; then
        log_info "创建环境配置文件..."
        cp .env.example .env
        log_warning "请编辑 .env 文件配置生产环境参数"
    else
        log_info "环境配置文件已存在"
    fi
}

# 构建镜像
build_images() {
    log_info "构建 Docker 镜像..."
    docker-compose build --no-cache
    log_success "镜像构建完成"
}

# 启动开发环境
start_dev() {
    log_info "启动开发环境..."
    docker-compose up -d
    log_success "开发环境启动完成"
    log_info "访问地址: http://localhost:8000"
    log_info "管理后台: http://localhost:8000/admin"
    log_info "默认管理员账号: admin/admin123"
}

# 启动生产环境
start_prod() {
    log_info "启动生产环境..."
    docker-compose -f docker-compose.prod.yml up -d
    log_success "生产环境启动完成"
    log_info "访问地址: http://localhost"
    log_info "HTTPS地址: https://localhost (需要配置SSL证书)"
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    docker-compose down
    docker-compose -f docker-compose.prod.yml down
    log_success "服务已停止"
}

# 查看日志
view_logs() {
    log_info "查看应用日志..."
    docker-compose logs -f web
}

# 数据库备份
backup_db() {
    log_info "备份数据库..."
    timestamp=$(date +%Y%m%d_%H%M%S)
    docker-compose exec db pg_dump -U cardverification cardverification > "backups/backup_${timestamp}.sql"
    log_success "数据库备份完成: backups/backup_${timestamp}.sql"
}

# 数据库恢复
restore_db() {
    if [ -z "$1" ]; then
        log_error "请指定备份文件路径"
        exit 1
    fi
    
    log_info "恢复数据库..."
    docker-compose exec -T db psql -U cardverification -d cardverification < "$1"
    log_success "数据库恢复完成"
}

# 清理系统
cleanup() {
    log_info "清理 Docker 系统..."
    docker system prune -f
    docker volume prune -f
    log_success "清理完成"
}

# 显示帮助信息
show_help() {
    echo "卡片验证系统 Docker 部署脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  dev         启动开发环境"
    echo "  prod        启动生产环境"
    echo "  stop        停止所有服务"
    echo "  restart     重启服务"
    echo "  logs        查看应用日志"
    echo "  backup      备份数据库"
    echo "  restore     恢复数据库 (需要指定备份文件)"
    echo "  cleanup     清理 Docker 系统"
    echo "  help        显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 dev                           # 启动开发环境"
    echo "  $0 prod                          # 启动生产环境"
    echo "  $0 restore backups/backup.sql    # 恢复数据库"
}

# 主函数
main() {
    case "$1" in
        "dev")
            check_docker
            create_directories
            setup_env
            build_images
            start_dev
            ;;
        "prod")
            check_docker
            create_directories
            setup_env
            build_images
            start_prod
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            sleep 2
            start_dev
            ;;
        "logs")
            view_logs
            ;;
        "backup")
            backup_db
            ;;
        "restore")
            restore_db "$2"
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"")
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
