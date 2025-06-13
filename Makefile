# ===== 卡片验证系统 Makefile =====
# 简化Docker操作的快捷命令

.PHONY: help build up down logs shell test clean backup

# 默认目标
.DEFAULT_GOAL := help

# 颜色定义
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
NC := \033[0m

# 帮助信息
help: ## 显示帮助信息
	@echo "$(BLUE)卡片验证系统 Docker 管理命令$(NC)"
	@echo ""
	@echo "$(YELLOW)基础命令:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# 构建镜像
build: ## 构建Docker镜像
	@echo "$(BLUE)构建Docker镜像...$(NC)"
	docker-compose build

# 强制重新构建
rebuild: ## 强制重新构建镜像（无缓存）
	@echo "$(BLUE)强制重新构建Docker镜像...$(NC)"
	docker-compose build --no-cache

# 启动服务（开发环境）
up: ## 启动开发环境服务
	@echo "$(BLUE)启动开发环境服务...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)服务启动完成！$(NC)"
	@echo "访问地址: http://localhost:8000"

# 启动生产环境
up-prod: ## 启动生产环境服务
	@echo "$(BLUE)启动生产环境服务...$(NC)"
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "$(GREEN)生产环境启动完成！$(NC)"

# 启动服务并显示日志
up-logs: ## 启动服务并显示日志
	@echo "$(BLUE)启动服务并显示日志...$(NC)"
	docker-compose up

# 停止服务
down: ## 停止所有服务
	@echo "$(BLUE)停止所有服务...$(NC)"
	docker-compose down

# 停止服务并删除卷
down-volumes: ## 停止服务并删除数据卷
	@echo "$(RED)警告: 这将删除所有数据！$(NC)"
	@read -p "确认删除所有数据? [y/N] " confirm && [ "$$confirm" = "y" ]
	docker-compose down -v

# 重启服务
restart: ## 重启所有服务
	@echo "$(BLUE)重启所有服务...$(NC)"
	docker-compose restart

# 查看服务状态
status: ## 查看服务状态
	@echo "$(BLUE)服务状态:$(NC)"
	docker-compose ps

# 查看日志
logs: ## 查看所有服务日志
	docker-compose logs -f

# 查看Web服务日志
logs-web: ## 查看Web服务日志
	docker-compose logs -f web

# 查看数据库日志
logs-db: ## 查看数据库日志
	docker-compose logs -f db

# 进入Web容器Shell
shell: ## 进入Web容器Shell
	docker-compose exec web bash

# 进入数据库Shell
shell-db: ## 进入数据库Shell
	docker-compose exec db psql -U cardverification -d cardverification

# Django管理命令
migrate: ## 运行数据库迁移
	@echo "$(BLUE)运行数据库迁移...$(NC)"
	docker-compose exec web python manage.py migrate

makemigrations: ## 创建数据库迁移文件
	@echo "$(BLUE)创建数据库迁移文件...$(NC)"
	docker-compose exec web python manage.py makemigrations

collectstatic: ## 收集静态文件
	@echo "$(BLUE)收集静态文件...$(NC)"
	docker-compose exec web python manage.py collectstatic --noinput

createsuperuser: ## 创建超级用户
	@echo "$(BLUE)创建超级用户...$(NC)"
	docker-compose exec web python manage.py createsuperuser

# 测试命令
test: ## 运行测试
	@echo "$(BLUE)运行测试...$(NC)"
	docker-compose exec web python manage.py test

test-coverage: ## 运行测试并生成覆盖率报告
	@echo "$(BLUE)运行测试覆盖率...$(NC)"
	docker-compose exec web coverage run --source='.' manage.py test
	docker-compose exec web coverage report

# 健康检查
health: ## 检查服务健康状态
	@echo "$(BLUE)检查服务健康状态...$(NC)"
	@curl -s http://localhost:8000/api/v1/health/ | python -m json.tool || echo "$(RED)健康检查失败$(NC)"

# 数据库备份
backup: ## 备份数据库
	@echo "$(BLUE)备份数据库...$(NC)"
	docker-compose --profile backup run --rm db-backup

# 清理系统
clean: ## 清理Docker系统
	@echo "$(BLUE)清理Docker系统...$(NC)"
	docker system prune -f

clean-all: ## 清理所有Docker资源
	@echo "$(RED)警告: 这将删除所有未使用的Docker资源！$(NC)"
	@read -p "确认清理所有资源? [y/N] " confirm && [ "$$confirm" = "y" ]
	docker system prune -a -f

# 开发环境设置
dev-setup: ## 设置开发环境
	@echo "$(BLUE)设置开发环境...$(NC)"
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(YELLOW)已创建.env文件，请编辑配置$(NC)"; \
	fi
	$(MAKE) build
	$(MAKE) up
	sleep 10
	$(MAKE) migrate
	@echo "$(GREEN)开发环境设置完成！$(NC)"

# 生产环境部署
prod-deploy: ## 部署生产环境
	@echo "$(BLUE)部署生产环境...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(RED)错误: .env文件不存在$(NC)"; \
		exit 1; \
	fi
	$(MAKE) build
	$(MAKE) up-prod
	sleep 15
	$(MAKE) migrate
	$(MAKE) collectstatic
	@echo "$(GREEN)生产环境部署完成！$(NC)"

# 监控相关
monitor: ## 启动监控服务
	@echo "$(BLUE)启动监控服务...$(NC)"
	docker-compose --profile monitoring up -d
	@echo "$(GREEN)监控服务启动完成！$(NC)"
	@echo "Prometheus: http://localhost:9090"

# Nginx相关
nginx: ## 启动Nginx反向代理
	@echo "$(BLUE)启动Nginx反向代理...$(NC)"
	docker-compose --profile nginx up -d
	@echo "$(GREEN)Nginx启动完成！$(NC)"
	@echo "访问地址: http://localhost"

# 显示有用的信息
info: ## 显示系统信息
	@echo "$(BLUE)系统信息:$(NC)"
	@echo "Docker版本: $$(docker --version)"
	@echo "Docker Compose版本: $$(docker-compose --version)"
	@echo ""
	@echo "$(BLUE)服务地址:$(NC)"
	@echo "主页:       http://localhost:8000/"
	@echo "管理后台:   http://localhost:8000/admin/"
	@echo "API文档:    http://localhost:8000/swagger/"
	@echo "健康检查:   http://localhost:8000/api/v1/health/"
