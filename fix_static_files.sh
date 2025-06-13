#!/bin/bash

# CardVerification 静态文件修复脚本
# 专门用于修复1Panel部署中的静态文件问题

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

# 检查当前目录
check_project_directory() {
    if [[ ! -f "manage.py" ]] && [[ ! -f "docker-compose.1panel.yml" ]]; then
        log_error "请在项目根目录运行此脚本"
        exit 1
    fi
}

# 检查静态文件目录
check_static_directories() {
    log_info "检查静态文件目录..."
    
    # 检查源静态文件目录
    if [[ ! -d "static" ]]; then
        log_warning "static 目录不存在，正在创建..."
        mkdir -p static
    fi
    
    # 检查收集目录
    if [[ ! -d "staticfiles" ]]; then
        log_warning "staticfiles 目录不存在，正在创建..."
        mkdir -p staticfiles
    fi
    
    # 设置权限
    chmod 755 static staticfiles
    
    log_success "静态文件目录检查完成"
}

# 重新收集静态文件
collect_static_files() {
    log_info "重新收集静态文件..."
    
    # 清空现有静态文件
    if [[ -d "staticfiles" ]]; then
        log_info "清空现有静态文件..."
        rm -rf staticfiles/*
    fi
    
    # 收集静态文件
    if docker-compose -f docker-compose.1panel.yml ps | grep -q "web.*Up"; then
        log_info "通过容器收集静态文件..."
        docker-compose -f docker-compose.1panel.yml exec web python manage.py collectstatic --noinput --clear
    else
        log_error "Web容器未运行，请先启动服务"
        exit 1
    fi
    
    log_success "静态文件收集完成"
}

# 检查静态文件内容
verify_static_files() {
    log_info "验证静态文件..."
    
    # 检查关键静态文件
    local key_files=(
        "staticfiles/admin/css/base.css"
        "staticfiles/css/style.css"
        "staticfiles/js/main.js"
    )
    
    local missing_files=()
    for file in "${key_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            missing_files+=("$file")
        fi
    done
    
    if [[ ${#missing_files[@]} -gt 0 ]]; then
        log_warning "以下关键静态文件缺失："
        for file in "${missing_files[@]}"; do
            echo "  - $file"
        done
    else
        log_success "关键静态文件验证通过"
    fi
    
    # 显示静态文件统计
    local file_count=$(find staticfiles -type f | wc -l)
    local total_size=$(du -sh staticfiles | cut -f1)
    log_info "静态文件统计: $file_count 个文件，总大小 $total_size"
}

# 显示1Panel配置建议
show_1panel_config() {
    log_info "1Panel 反向代理配置建议："
    echo
    echo "在1Panel网站配置中添加以下Nginx配置："
    echo
    echo "# 静态文件代理"
    echo "location /static/ {"
    echo "    alias $(pwd)/staticfiles/;"
    echo "    expires 30d;"
    echo "    add_header Cache-Control \"public, immutable\";"
    echo "    "
    echo "    # 启用 gzip 压缩"
    echo "    gzip on;"
    echo "    gzip_types text/css application/javascript text/javascript application/json;"
    echo "}"
    echo
    echo "# 媒体文件代理"
    echo "location /media/ {"
    echo "    alias $(pwd)/media/;"
    echo "    expires 7d;"
    echo "    add_header Cache-Control \"public\";"
    echo "}"
    echo
    log_warning "注意：使用 alias 直接映射到宿主机目录，而不是 proxy_pass"
}

# 测试静态文件访问
test_static_access() {
    log_info "测试静态文件访问..."
    
    # 测试容器内部访问
    if docker-compose -f docker-compose.1panel.yml exec web curl -f http://localhost:8000/static/admin/css/base.css >/dev/null 2>&1; then
        log_success "容器内部静态文件访问正常"
    else
        log_warning "容器内部静态文件访问失败"
    fi
    
    # 测试外部访问（如果配置了域名）
    if [[ -n "${DOMAIN:-}" ]]; then
        if curl -f "https://${DOMAIN}/static/admin/css/base.css" >/dev/null 2>&1; then
            log_success "外部静态文件访问正常"
        else
            log_warning "外部静态文件访问失败，请检查1Panel反向代理配置"
        fi
    fi
}

# 重启相关服务
restart_services() {
    log_info "重启Web服务..."
    docker-compose -f docker-compose.1panel.yml restart web
    
    # 等待服务启动
    sleep 5
    
    # 检查服务状态
    if docker-compose -f docker-compose.1panel.yml ps | grep -q "web.*Up"; then
        log_success "Web服务重启成功"
    else
        log_error "Web服务重启失败"
        exit 1
    fi
}

# 主函数
main() {
    log_info "开始修复静态文件问题..."
    
    check_project_directory
    check_static_directories
    collect_static_files
    verify_static_files
    restart_services
    test_static_access
    show_1panel_config
    
    log_success "静态文件修复完成！"
    echo
    log_info "后续步骤："
    echo "1. 在1Panel中更新网站的反向代理配置"
    echo "2. 清理浏览器缓存并强制刷新页面"
    echo "3. 检查网站静态文件是否正常加载"
}

# 执行主函数
main "$@"
