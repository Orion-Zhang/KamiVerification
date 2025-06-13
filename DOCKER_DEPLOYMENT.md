# 卡片验证系统 Docker 部署指南

本文档介绍如何使用 Docker 部署卡片验证系统。

## 📋 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- Git

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd CardVerification
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量文件
nano .env
```

### 3. 启动开发环境

```bash
# 使用部署脚本（推荐）
chmod +x deploy.sh
./deploy.sh dev

# 或者直接使用 docker-compose
docker-compose up -d
```

### 4. 访问应用

- 应用地址: http://localhost:8000
- 管理后台: http://localhost:8000/admin
- API 文档: http://localhost:8000/api/docs/
- 默认管理员: admin/admin123

## 🏗️ 项目结构

```
CardVerification/
├── docker-compose.yml          # 开发环境配置
├── docker-compose.prod.yml     # 生产环境配置
├── Dockerfile                  # 应用镜像构建文件
├── .dockerignore              # Docker 忽略文件
├── entrypoint.sh              # 容器启动脚本
├── nginx.conf                 # Nginx 开发环境配置
├── nginx.prod.conf            # Nginx 生产环境配置
├── .env.example               # 环境变量模板
├── deploy.sh                  # 部署脚本
└── requirements.txt           # Python 依赖
```

## 🔧 部署脚本使用

部署脚本 `deploy.sh` 提供了便捷的部署和管理功能：

```bash
# 启动开发环境
./deploy.sh dev

# 启动生产环境
./deploy.sh prod

# 停止所有服务
./deploy.sh stop

# 重启服务
./deploy.sh restart

# 查看应用日志
./deploy.sh logs

# 备份数据库
./deploy.sh backup

# 恢复数据库
./deploy.sh restore backups/backup_20240101_120000.sql

# 清理 Docker 系统
./deploy.sh cleanup

# 显示帮助信息
./deploy.sh help
```

## 🌐 服务组件

### 开发环境 (docker-compose.yml)

- **web**: Django 应用服务 (端口 8000)
- **db**: PostgreSQL 数据库 (端口 5432)
- **redis**: Redis 缓存服务 (端口 6379)
- **nginx**: Nginx 反向代理 (端口 80)

### 生产环境 (docker-compose.prod.yml)

- **web**: Django 应用服务 (优化配置)
- **db**: PostgreSQL 数据库 (持久化存储)
- **redis**: Redis 缓存服务 (持久化配置)
- **nginx**: Nginx 反向代理 (HTTPS + 安全配置)
- **db_backup**: 自动数据库备份服务

## 🔒 生产环境配置

### 1. 环境变量配置

编辑 `.env` 文件，设置生产环境参数：

```bash
# 关闭调试模式
DEBUG=0

# 设置强密钥
SECRET_KEY=your-super-secret-key-here

# 设置允许的主机
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# 数据库密码
POSTGRES_PASSWORD=your-strong-password

# Redis 密码
REDIS_PASSWORD=your-redis-password
```

### 2. SSL 证书配置

将 SSL 证书文件放置在 `ssl/` 目录：

```bash
ssl/
├── cert.pem    # SSL 证书
└── key.pem     # 私钥文件
```

### 3. 启动生产环境

```bash
./deploy.sh prod
```

## 📊 监控和维护

### 查看服务状态

```bash
docker-compose ps
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs web
docker-compose logs db
docker-compose logs nginx
```

### 进入容器

```bash
# 进入 Django 应用容器
docker-compose exec web bash

# 进入数据库容器
docker-compose exec db psql -U cardverification
```

### 数据库管理

```bash
# 执行数据库迁移
docker-compose exec web python manage.py migrate

# 创建超级用户
docker-compose exec web python manage.py createsuperuser

# 收集静态文件
docker-compose exec web python manage.py collectstatic
```

## 🔄 更新部署

### 1. 更新代码

```bash
git pull origin main
```

### 2. 重新构建镜像

```bash
docker-compose build --no-cache
```

### 3. 重启服务

```bash
./deploy.sh restart
```

## 🛠️ 故障排除

### 常见问题

1. **端口冲突**
   ```bash
   # 检查端口占用
   netstat -tulpn | grep :8000
   
   # 修改 docker-compose.yml 中的端口映射
   ```

2. **权限问题**
   ```bash
   # 给脚本执行权限
   chmod +x deploy.sh
   chmod +x entrypoint.sh
   ```

3. **数据库连接失败**
   ```bash
   # 检查数据库服务状态
   docker-compose logs db
   
   # 重启数据库服务
   docker-compose restart db
   ```

4. **静态文件不显示**
   ```bash
   # 重新收集静态文件
   docker-compose exec web python manage.py collectstatic --noinput
   ```

### 清理和重置

```bash
# 停止并删除所有容器
docker-compose down -v

# 清理 Docker 系统
./deploy.sh cleanup

# 重新开始
./deploy.sh dev
```

## 📝 注意事项

1. **生产环境安全**
   - 修改默认密码
   - 配置防火墙
   - 定期更新系统
   - 监控日志文件

2. **数据备份**
   - 定期备份数据库
   - 备份媒体文件
   - 测试恢复流程

3. **性能优化**
   - 根据负载调整 worker 数量
   - 配置适当的缓存策略
   - 监控资源使用情况

## 📞 支持

如有问题，请查看：
- 项目文档
- Docker 官方文档
- Django 部署指南
