#!/bin/bash

# CardVerification 1Panel 快速启动脚本
# 一键完成所有配置和部署

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# 显示欢迎信息
show_welcome() {
    clear
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║           🚀 CardVerification 1Panel 快速部署                ║"
    echo "║                                                              ║"
    echo "║                  专为 1Panel + OpenResty 优化                ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo
}

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

# 检查系统要求
check_requirements() {
    log_info "检查系统要求..."
    
    # 检查是否为root用户或有sudo权限
    if [[ $EUID -eq 0 ]]; then
        log_success "以root用户运行"
    elif sudo -n true 2>/dev/null; then
        log_success "具有sudo权限"
    else
        log_error "需要root权限或sudo权限"
        exit 1
    fi
    
    # 检查Docker
    if command -v docker &> /dev/null; then
        log_success "Docker 已安装"
    else
        log_error "Docker 未安装，请先安装Docker"
        exit 1
    fi
    
    # 检查Docker Compose
    if command -v docker-compose &> /dev/null; then
        log_success "Docker Compose 已安装"
    else
        log_error "Docker Compose 未安装，请先安装Docker Compose"
        exit 1
    fi
    
    # 检查Git
    if command -v git &> /dev/null; then
        log_success "Git 已安装"
    else
        log_warning "Git 未安装，某些功能可能受限"
    fi
}

# 配置环境变量
configure_environment() {
    log_info "配置环境变量..."
    
    if [[ ! -f ".env" ]]; then
        if [[ -f ".env.1panel.example" ]]; then
            cp .env.1panel.example .env
            log_success "已复制环境配置模板"
        else
            log_error "环境配置模板不存在"
            exit 1
        fi
    fi
    
    # 生成随机SECRET_KEY
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    sed -i "s/your-super-secure-secret-key-here-change-this/$SECRET_KEY/" .env
    
    # 生成随机数据库密码
    DB_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))")
    sed -i "s/your-secure-db-password/$DB_PASSWORD/" .env
    
    log_success "环境变量配置完成"
}

# 设置文件权限
set_permissions() {
    log_info "设置文件权限..."
    
    # 设置脚本执行权限
    chmod +x deploy_1panel.sh manage_1panel.sh quick_start_1panel.sh
    
    # 创建必要目录
    mkdir -p logs media staticfiles backups
    chmod 755 logs media staticfiles backups
    
    log_success "文件权限设置完成"
}

# 执行部署
deploy_application() {
    log_info "开始部署应用..."
    
    # 执行部署脚本
    ./deploy_1panel.sh
    
    log_success "应用部署完成"
}

# 配置检查
run_config_check() {
    log_info "运行配置检查..."
    
    if command -v python3 &> /dev/null; then
        python3 check_1panel_config.py
    else
        log_warning "Python3 未安装，跳过配置检查"
    fi
}

# 显示部署结果
show_deployment_result() {
    echo
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                              ║${NC}"
    echo -e "${GREEN}║                    🎉 部署完成！                             ║${NC}"
    echo -e "${GREEN}║                                                              ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    log_info "部署信息:"
    echo "  📱 应用端口: 127.0.0.1:8000"
    echo "  🌐 域名: kami.killua.tech"
    echo "  🔒 SSL: 需要在1Panel中配置"
    echo
    
    log_info "下一步操作:"
    echo "  1. 在1Panel中创建网站 kami.killua.tech"
    echo "  2. 配置反向代理到 http://127.0.0.1:8000"
    echo "  3. 申请并配置SSL证书"
    echo "  4. 访问 https://kami.killua.tech 测试"
    echo
    
    log_info "管理命令:"
    echo "  ./manage_1panel.sh status    # 查看状态"
    echo "  ./manage_1panel.sh logs      # 查看日志"
    echo "  ./manage_1panel.sh health    # 健康检查"
    echo "  ./manage_1panel.sh 1panel-info # 1Panel配置信息"
    echo
    
    log_info "访问地址:"
    echo "  🏠 主页: https://kami.killua.tech"
    echo "  ⚙️  管理后台: https://kami.killua.tech/admin/"
    echo "  📚 API文档: https://kami.killua.tech/swagger/"
}

# 询问用户确认
ask_confirmation() {
    echo
    log_warning "即将开始1Panel环境部署，这将："
    echo "  - 创建Docker容器（PostgreSQL + Redis + Django）"
    echo "  - 配置环境变量和安全设置"
    echo "  - 初始化数据库和收集静态文件"
    echo "  - 绑定到本地端口 127.0.0.1:8000"
    echo
    
    read -p "确认继续部署？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "部署已取消"
        exit 0
    fi
}

# 主函数
main() {
    show_welcome
    
    log_info "开始CardVerification 1Panel环境快速部署"
    echo
    
    check_requirements
    echo
    
    ask_confirmation
    echo
    
    configure_environment
    echo
    
    set_permissions
    echo
    
    deploy_application
    echo
    
    run_config_check
    echo
    
    show_deployment_result
}

# 执行主函数
main "$@"
