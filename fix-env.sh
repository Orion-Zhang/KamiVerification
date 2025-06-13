#!/bin/bash

# ===== 环境变量文件修复脚本 =====
# 修复.env文件中的语法问题

set -e

# 颜色输出
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

# 修复.env文件
fix_env_file() {
    local env_file="$1"
    
    if [ ! -f "$env_file" ]; then
        log_error "文件 $env_file 不存在"
        return 1
    fi
    
    log_info "修复 $env_file 文件..."
    
    # 创建备份
    cp "$env_file" "${env_file}.backup"
    log_info "已创建备份文件: ${env_file}.backup"
    
    # 修复常见问题
    sed -i 's/SYSTEM_NAME=Killua 卡密系统/SYSTEM_NAME="Killua Card System"/g' "$env_file"
    sed -i 's/SYSTEM_DESCRIPTION=专业的卡密验证管理系统/SYSTEM_DESCRIPTION="Professional Card Verification System"/g' "$env_file"
    
    # 确保所有包含空格或特殊字符的值都被引号包围
    sed -i 's/^\([A-Z_]*=\)\([^"#]*[[:space:]][^"#]*\)$/\1"\2"/g' "$env_file"
    
    log_success "文件修复完成"
}

# 验证.env文件语法
validate_env_file() {
    local env_file="$1"
    
    log_info "验证 $env_file 文件语法..."
    
    # 尝试source文件
    if bash -n "$env_file" 2>/dev/null; then
        log_success "文件语法正确"
        return 0
    else
        log_error "文件语法仍有问题"
        return 1
    fi
}

# 创建简化的生产环境配置
create_simple_env() {
    log_info "创建简化的.env文件..."
    
    cat > .env << 'EOF'
# Django 核心配置
SECRET_KEY=django-insecure-change-this-key-in-production-environment
DEBUG=0
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_SETTINGS_MODULE=CardVerification.settings

# 数据库配置
POSTGRES_DB=cardverification
POSTGRES_USER=cardverification
POSTGRES_PASSWORD=strongpassword123
DATABASE_URL=postgresql://cardverification:strongpassword123@db:5432/cardverification

# Redis 配置
REDIS_PASSWORD=redispassword123
REDIS_URL=redis://:redispassword123@redis:6379/0

# 超级用户配置
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=adminpassword123

# 应用配置
SYSTEM_NAME="Killua Card System"
SYSTEM_VERSION=1.0.0
SYSTEM_DESCRIPTION="Professional Card Verification System"

# 生产环境优化
GUNICORN_WORKERS=3
GUNICORN_TIMEOUT=120

# 时区配置
TIME_ZONE=Asia/Shanghai
LANGUAGE_CODE=zh-hans
EOF
    
    log_success "已创建简化的.env文件"
    log_warning "请根据需要修改密码和配置！"
}

# 主函数
main() {
    echo -e "${BLUE}=== 环境变量文件修复工具 ===${NC}"
    
    if [ -f ".env" ]; then
        log_info "发现现有.env文件，尝试修复..."
        fix_env_file ".env"
        
        if ! validate_env_file ".env"; then
            log_warning "修复失败，创建新的简化配置文件..."
            create_simple_env
        fi
    else
        log_info "未发现.env文件，创建新的配置文件..."
        create_simple_env
    fi
    
    echo ""
    echo -e "${GREEN}修复完成！${NC}"
    echo -e "${YELLOW}重要提醒：${NC}"
    echo "1. 请检查并修改.env文件中的密码"
    echo "2. 确保SECRET_KEY、POSTGRES_PASSWORD、REDIS_PASSWORD都已修改"
    echo "3. 根据需要调整ALLOWED_HOSTS"
    echo ""
    echo "现在可以重新运行部署命令："
    echo "  ./deploy.sh -e prod"
}

# 执行主函数
main "$@"
