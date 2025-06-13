#!/bin/bash

# ===== 卡片验证系统 Docker 部署脚本 =====
# 自动化部署脚本，支持开发和生产环境

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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

log_header() {
    echo -e "${PURPLE}=== $1 ===${NC}"
}

# 显示帮助信息
show_help() {
    echo -e "${CYAN}卡片验证系统 Docker 部署脚本${NC}"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -e, --env ENV        部署环境 (dev|prod) [默认: dev]"
    echo "  -p, --profile PROFILE 启用的服务配置 (nginx|monitoring|backup)"
    echo "  -c, --clean          清理现有容器和卷"
    echo "  -b, --build          强制重新构建镜像"
    echo "  -h, --help           显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                   # 开发环境部署"
    echo "  $0 -e prod           # 生产环境部署"
    echo "  $0 -e prod -p nginx  # 生产环境 + Nginx"
    echo "  $0 -c -b             # 清理并重新构建"
}

# 检查Docker环境
check_docker() {
    log_header "检查Docker环境"
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    log_info "Docker版本: $(docker --version)"
    log_info "Docker Compose版本: $(docker-compose --version)"
    
    # 检查Docker服务状态
    if ! docker info &> /dev/null; then
        log_error "Docker服务未运行，请启动Docker服务"
        exit 1
    fi
    
    log_success "Docker环境检查通过"
}

# 检查环境变量文件
check_env_file() {
    log_header "检查环境配置"
    
    if [ ! -f ".env" ]; then
        log_warning ".env文件不存在，从模板创建..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_success "已创建.env文件，请编辑配置后重新运行"
            log_warning "重要：请修改.env文件中的密码和密钥！"
            exit 0
        else
            log_error ".env.example文件不存在"
            exit 1
        fi
    fi
    
    # 检查关键配置项
    set -a  # 自动导出变量
    source .env 2>/dev/null || {
        log_error ".env文件格式错误，请检查语法"
        exit 1
    }
    set +a  # 关闭自动导出

    if [ "$SECRET_KEY" = "your-super-secret-key-change-this-in-production" ]; then
        log_error "请修改.env文件中的SECRET_KEY"
        exit 1
    fi

    if [ "$POSTGRES_PASSWORD" = "your-strong-database-password" ]; then
        log_error "请修改.env文件中的POSTGRES_PASSWORD"
        exit 1
    fi
    
    log_success "环境配置检查通过"
}

# 清理现有部署
clean_deployment() {
    log_header "清理现有部署"
    
    log_info "停止所有服务..."
    docker-compose down -v --remove-orphans || true
    
    if [ "$CLEAN_VOLUMES" = "true" ]; then
        log_warning "删除所有数据卷（数据将丢失）..."
        docker volume prune -f || true
    fi
    
    if [ "$CLEAN_IMAGES" = "true" ]; then
        log_info "删除构建的镜像..."
        docker-compose down --rmi all || true
    fi
    
    log_success "清理完成"
}

# 构建镜像
build_images() {
    log_header "构建Docker镜像"
    
    BUILD_ARGS=""
    if [ "$FORCE_BUILD" = "true" ]; then
        BUILD_ARGS="--no-cache"
    fi
    
    log_info "构建应用镜像..."
    docker-compose build $BUILD_ARGS
    
    log_success "镜像构建完成"
}

# 部署服务
deploy_services() {
    log_header "部署服务"
    
    # 构建compose命令
    COMPOSE_CMD="docker-compose"
    
    # 添加生产环境配置
    if [ "$ENVIRONMENT" = "prod" ]; then
        COMPOSE_CMD="$COMPOSE_CMD -f docker-compose.yml -f docker-compose.prod.yml"
    fi
    
    # 添加profile配置
    if [ -n "$PROFILE" ]; then
        COMPOSE_CMD="$COMPOSE_CMD --profile $PROFILE"
    fi
    
    log_info "启动服务..."
    log_info "执行命令: $COMPOSE_CMD up -d"
    
    eval "$COMPOSE_CMD up -d"
    
    log_success "服务启动完成"
}

# 等待服务就绪
wait_for_services() {
    log_header "等待服务就绪"
    
    log_info "等待数据库服务..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if docker-compose exec -T db pg_isready -U cardverification &> /dev/null; then
            log_success "数据库服务就绪"
            break
        fi
        sleep 2
        timeout=$((timeout-2))
    done
    
    if [ $timeout -le 0 ]; then
        log_error "数据库服务启动超时"
        exit 1
    fi
    
    log_info "等待应用服务..."
    timeout=120
    while [ $timeout -gt 0 ]; do
        if curl -s http://localhost:8000/api/v1/health/ &> /dev/null; then
            log_success "应用服务就绪"
            break
        fi
        sleep 5
        timeout=$((timeout-5))
    done
    
    if [ $timeout -le 0 ]; then
        log_error "应用服务启动超时"
        exit 1
    fi
}

# 显示部署信息
show_deployment_info() {
    log_header "部署信息"
    
    echo -e "${CYAN}🎉 部署完成！${NC}"
    echo ""
    echo -e "${YELLOW}访问地址：${NC}"
    echo "  🏠 主页:           http://localhost:8000/"
    echo "  🔧 管理后台:       http://localhost:8000/admin/"
    echo "  📊 控制面板:       http://localhost:8000/dashboard/"
    echo "  📚 API文档:        http://localhost:8000/swagger/"
    echo "  ⚕️ 健康检查:       http://localhost:8000/api/v1/health/"
    
    if [ "$PROFILE" = "nginx" ]; then
        echo "  🌐 Nginx代理:      http://localhost/"
    fi
    
    if [ "$PROFILE" = "monitoring" ]; then
        echo "  📈 监控面板:       http://localhost:9090/"
    fi
    
    echo ""
    echo -e "${YELLOW}管理命令：${NC}"
    echo "  查看服务状态:      docker-compose ps"
    echo "  查看日志:          docker-compose logs -f"
    echo "  停止服务:          docker-compose down"
    echo "  重启服务:          docker-compose restart"
    echo ""
    echo -e "${YELLOW}默认管理员账户：${NC}"
    source .env
    echo "  用户名: ${DJANGO_SUPERUSER_USERNAME:-admin}"
    echo "  邮箱:   ${DJANGO_SUPERUSER_EMAIL:-admin@example.com}"
    echo "  密码:   ${DJANGO_SUPERUSER_PASSWORD:-请查看.env文件}"
}

# 主函数
main() {
    # 默认参数
    ENVIRONMENT="dev"
    PROFILE=""
    CLEAN_DEPLOYMENT=false
    CLEAN_VOLUMES=false
    CLEAN_IMAGES=false
    FORCE_BUILD=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--env)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -p|--profile)
                PROFILE="$2"
                shift 2
                ;;
            -c|--clean)
                CLEAN_DEPLOYMENT=true
                CLEAN_VOLUMES=true
                shift
                ;;
            -b|--build)
                FORCE_BUILD=true
                shift
                ;;
            -h|--help)
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
    
    # 验证环境参数
    if [ "$ENVIRONMENT" != "dev" ] && [ "$ENVIRONMENT" != "prod" ]; then
        log_error "无效的环境参数: $ENVIRONMENT (支持: dev, prod)"
        exit 1
    fi
    
    log_header "卡片验证系统 Docker 部署"
    log_info "部署环境: $ENVIRONMENT"
    if [ -n "$PROFILE" ]; then
        log_info "服务配置: $PROFILE"
    fi
    
    # 执行部署流程
    check_docker
    check_env_file
    
    if [ "$CLEAN_DEPLOYMENT" = "true" ]; then
        clean_deployment
    fi
    
    build_images
    deploy_services
    wait_for_services
    show_deployment_info
}

# 执行主函数
main "$@"
