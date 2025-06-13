#!/bin/bash

# CardVerification SSL连接问题修复脚本
# 解决 "server does not support SSL, but SSL was required" 错误

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

# 检查是否存在.env文件
check_env_file() {
    log_info "检查环境配置文件..."
    
    if [[ ! -f ".env" ]]; then
        if [[ -f ".env.1panel.example" ]]; then
            log_warning ".env文件不存在，正在从模板创建..."
            cp .env.1panel.example .env
            log_success "已创建.env文件"
        else
            log_error ".env.1panel.example模板文件不存在"
            exit 1
        fi
    else
        log_success ".env文件已存在"
    fi
}

# 修复SSL配置
fix_ssl_config() {
    log_info "修复数据库SSL配置..."
    
    # 检查是否已有DB_SSLMODE配置
    if grep -q "^DB_SSLMODE=" .env; then
        current_mode=$(grep "^DB_SSLMODE=" .env | cut -d'=' -f2)
        log_info "当前SSL模式: $current_mode"
        
        if [[ "$current_mode" == "require" ]]; then
            log_warning "检测到强制SSL模式，正在修改为prefer模式..."
            sed -i 's/^DB_SSLMODE=require/DB_SSLMODE=prefer/' .env
            log_success "已修改SSL模式为prefer"
        else
            log_success "SSL模式配置正常"
        fi
    else
        log_warning "未找到DB_SSLMODE配置，正在添加..."
        echo "" >> .env
        echo "# 数据库SSL模式 (Docker环境建议使用 prefer)" >> .env
        echo "DB_SSLMODE=prefer" >> .env
        log_success "已添加DB_SSLMODE=prefer配置"
    fi
}

# 验证配置
verify_config() {
    log_info "验证配置..."
    
    # 检查必要的环境变量
    required_vars=("SECRET_KEY" "POSTGRES_DB" "POSTGRES_USER" "POSTGRES_PASSWORD")
    
    for var in "${required_vars[@]}"; do
        if grep -q "^${var}=" .env && ! grep -q "your-" .env | grep -q "$var"; then
            log_success "$var 已配置"
        else
            log_warning "$var 需要手动配置"
        fi
    done
}

# 重启服务
restart_services() {
    log_info "重启Docker服务..."
    
    if [[ -f "docker-compose.1panel.yml" ]]; then
        docker-compose -f docker-compose.1panel.yml down
        docker-compose -f docker-compose.1panel.yml up -d
        log_success "服务已重启"
    else
        log_error "docker-compose.1panel.yml文件不存在"
        exit 1
    fi
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    
    # 等待服务启动
    sleep 10
    
    # 检查数据库连接
    if docker-compose -f docker-compose.1panel.yml exec -T db pg_isready -U ${POSTGRES_USER:-cardverification} >/dev/null 2>&1; then
        log_success "数据库连接正常"
    else
        log_warning "数据库连接检查失败，请查看日志"
    fi
    
    # 检查应用健康状态
    if curl -f http://127.0.0.1:8000/api/v1/health/ >/dev/null 2>&1; then
        log_success "应用服务正常"
    else
        log_warning "应用服务检查失败，请查看日志"
    fi
}

# 显示帮助信息
show_help() {
    echo "CardVerification SSL连接问题修复脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --check-only    只检查配置，不修改"
    echo "  --no-restart    修复配置但不重启服务"
    echo "  --help         显示此帮助信息"
    echo ""
    echo "此脚本将："
    echo "1. 检查并创建.env文件"
    echo "2. 修复数据库SSL配置"
    echo "3. 重启Docker服务"
    echo "4. 验证服务状态"
}

# 主函数
main() {
    echo "🔧 CardVerification SSL连接问题修复工具"
    echo "=========================================="
    echo ""
    
    # 解析命令行参数
    CHECK_ONLY=false
    NO_RESTART=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --check-only)
                CHECK_ONLY=true
                shift
                ;;
            --no-restart)
                NO_RESTART=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 执行修复步骤
    check_env_file
    
    if [[ "$CHECK_ONLY" == "false" ]]; then
        fix_ssl_config
    fi
    
    verify_config
    
    if [[ "$CHECK_ONLY" == "false" && "$NO_RESTART" == "false" ]]; then
        restart_services
        check_services
    fi
    
    echo ""
    log_success "修复完成！"
    echo ""
    echo "如果问题仍然存在，请："
    echo "1. 检查Docker容器日志: docker-compose -f docker-compose.1panel.yml logs"
    echo "2. 查看应用日志: ./manage_1panel.sh logs"
    echo "3. 手动检查.env文件配置"
}

# 运行主函数
main "$@"
