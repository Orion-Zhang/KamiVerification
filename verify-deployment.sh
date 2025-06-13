#!/bin/bash

# ===== 部署验证脚本 =====
# 验证Docker部署是否成功

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

log_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# 验证函数
verify_docker() {
    log_header "验证Docker环境"
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装"
        return 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker服务未运行"
        return 1
    fi
    
    log_success "Docker环境正常"
    return 0
}

verify_services() {
    log_header "验证服务状态"
    
    # 检查容器状态
    local containers=("cardverification_web" "cardverification_db" "cardverification_redis")
    
    for container in "${containers[@]}"; do
        if docker ps --format "table {{.Names}}" | grep -q "$container"; then
            local status=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "unknown")
            if [ "$status" = "healthy" ] || [ "$status" = "unknown" ]; then
                log_success "容器 $container 运行正常"
            else
                log_warning "容器 $container 状态: $status"
            fi
        else
            log_error "容器 $container 未运行"
            return 1
        fi
    done
    
    return 0
}

verify_database() {
    log_header "验证数据库连接"
    
    if docker-compose exec -T db pg_isready -U cardverification &> /dev/null; then
        log_success "数据库连接正常"
        
        # 检查数据库表
        local table_count=$(docker-compose exec -T db psql -U cardverification -d cardverification -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')
        
        if [ "$table_count" -gt 0 ]; then
            log_success "数据库表已创建 ($table_count 个表)"
        else
            log_warning "数据库表未创建，可能需要运行迁移"
        fi
        
        return 0
    else
        log_error "数据库连接失败"
        return 1
    fi
}

verify_redis() {
    log_header "验证Redis连接"
    
    if docker-compose exec -T redis redis-cli ping &> /dev/null; then
        log_success "Redis连接正常"
        return 0
    else
        log_error "Redis连接失败"
        return 1
    fi
}

verify_web_app() {
    log_header "验证Web应用"
    
    local base_url="http://localhost:8000"
    local max_attempts=30
    local attempt=1
    
    log_info "等待Web应用启动..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$base_url/api/v1/health/" &> /dev/null; then
            log_success "Web应用启动成功"
            break
        fi
        
        log_info "尝试 $attempt/$max_attempts - 等待Web应用..."
        sleep 5
        attempt=$((attempt + 1))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        log_error "Web应用启动超时"
        return 1
    fi
    
    # 测试各个端点
    local endpoints=(
        "/api/v1/health/"
        "/"
        "/admin/"
        "/dashboard/"
    )
    
    for endpoint in "${endpoints[@]}"; do
        local url="$base_url$endpoint"
        local status_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")
        
        if [ "$status_code" -eq 200 ] || [ "$status_code" -eq 302 ] || [ "$status_code" -eq 301 ]; then
            log_success "端点 $endpoint 响应正常 ($status_code)"
        else
            log_warning "端点 $endpoint 响应异常 ($status_code)"
        fi
    done
    
    return 0
}

verify_api() {
    log_header "验证API功能"
    
    local health_url="http://localhost:8000/api/v1/health/"
    
    log_info "测试健康检查API..."
    local response=$(curl -s "$health_url" || echo "")
    
    if echo "$response" | grep -q '"status": "healthy"'; then
        log_success "健康检查API正常"
        
        # 显示API响应信息
        if command -v python3 &> /dev/null; then
            echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
        else
            echo "$response"
        fi
        
        return 0
    else
        log_error "健康检查API异常"
        echo "响应: $response"
        return 1
    fi
}

show_deployment_summary() {
    log_header "部署摘要"
    
    echo -e "${GREEN}🎉 部署验证完成！${NC}"
    echo ""
    echo -e "${YELLOW}服务访问地址：${NC}"
    echo "  🏠 主页:           http://localhost:8000/"
    echo "  🔧 管理后台:       http://localhost:8000/admin/"
    echo "  📊 控制面板:       http://localhost:8000/dashboard/"
    echo "  📚 API文档:        http://localhost:8000/swagger/"
    echo "  ⚕️ 健康检查:       http://localhost:8000/api/v1/health/"
    echo ""
    echo -e "${YELLOW}常用管理命令：${NC}"
    echo "  查看服务状态:      docker-compose ps"
    echo "  查看日志:          docker-compose logs -f"
    echo "  进入容器:          docker-compose exec web bash"
    echo "  停止服务:          docker-compose down"
    echo ""
    echo -e "${YELLOW}使用Makefile快捷命令：${NC}"
    echo "  make help         # 查看所有可用命令"
    echo "  make status       # 查看服务状态"
    echo "  make logs         # 查看日志"
    echo "  make shell        # 进入容器"
}

# 主函数
main() {
    log_header "卡片验证系统部署验证"
    
    local failed=0
    
    # 执行各项验证
    verify_docker || failed=1
    verify_services || failed=1
    verify_database || failed=1
    verify_redis || failed=1
    verify_web_app || failed=1
    verify_api || failed=1
    
    if [ $failed -eq 0 ]; then
        show_deployment_summary
        exit 0
    else
        log_error "部署验证失败，请检查错误信息"
        echo ""
        echo -e "${YELLOW}故障排除建议：${NC}"
        echo "1. 检查Docker服务是否正常运行"
        echo "2. 查看服务日志: docker-compose logs"
        echo "3. 检查端口是否被占用: netstat -tlnp | grep 8000"
        echo "4. 重新构建并启动: docker-compose down && docker-compose up --build -d"
        exit 1
    fi
}

# 执行主函数
main "$@"
