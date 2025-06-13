# 🐳 Docker 部署指南

本文档详细介绍如何使用Docker部署卡片验证系统。

## 📋 部署前准备

### 1. 系统要求
- Docker Engine 20.10+
- Docker Compose 2.0+
- 至少 2GB 可用内存
- 至少 10GB 可用磁盘空间

### 2. 检查Docker环境
```bash
# 检查Docker版本
docker --version
docker-compose --version

# 检查Docker服务状态
docker info
```

## 🚀 快速部署

### 1. 克隆项目
```bash
git clone <your-repository-url>
cd CardVerification
```

### 2. 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量（重要！）
nano .env
```

**必须修改的配置项：**
```bash
# Django密钥 - 生产环境必须修改！
SECRET_KEY=your-super-secret-key-change-this-in-production

# 数据库密码
POSTGRES_PASSWORD=your-strong-database-password

# Redis密码
REDIS_PASSWORD=your-redis-password

# 超级用户配置
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@yourdomain.com
DJANGO_SUPERUSER_PASSWORD=your-admin-password

# 允许的主机
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
```

### 3. 启动服务
```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 4. 验证部署
```bash
# 健康检查
curl http://localhost:8000/api/v1/health/

# 访问管理后台
# http://localhost:8000/admin/

# 访问前端界面
# http://localhost:8000/
```

## 🔧 高级配置

### 1. 生产环境部署
```bash
# 使用生产环境配置
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 启用Nginx反向代理
docker-compose --profile nginx up -d
```

### 2. 启用监控
```bash
# 启用Prometheus监控
docker-compose --profile monitoring up -d

# 访问监控面板
# http://localhost:9090/
```

### 3. 数据库备份
```bash
# 手动备份
docker-compose --profile backup run --rm db-backup

# 设置定时备份（crontab）
0 2 * * * cd /path/to/CardVerification && docker-compose --profile backup run --rm db-backup
```

## 📊 服务说明

### 核心服务
| 服务名 | 端口 | 说明 |
|--------|------|------|
| web | 8000 | Django应用服务 |
| db | 5432 | PostgreSQL数据库 |
| redis | 6379 | Redis缓存服务 |

### 可选服务
| 服务名 | 端口 | 说明 | Profile |
|--------|------|------|---------|
| nginx | 80/443 | 反向代理服务 | nginx |
| monitoring | 9090 | Prometheus监控 | monitoring |
| db-backup | - | 数据库备份 | backup |

## 🔍 故障排除

### 1. 常见问题

#### 服务启动失败
```bash
# 查看详细日志
docker-compose logs <service-name>

# 重新构建镜像
docker-compose build --no-cache

# 清理并重启
docker-compose down -v
docker-compose up -d
```

#### 数据库连接失败
```bash
# 检查数据库服务状态
docker-compose exec db pg_isready -U cardverification

# 查看数据库日志
docker-compose logs db

# 重置数据库
docker-compose down -v
docker volume rm cardverification_postgres_data
docker-compose up -d
```

#### 权限问题
```bash
# 修复文件权限
sudo chown -R $USER:$USER .
chmod +x docker-entrypoint.sh
chmod +x docker/scripts/backup.sh
```

### 2. 性能优化

#### 调整资源限制
编辑 `docker-compose.prod.yml`：
```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
```

#### 数据库优化
```bash
# 调整PostgreSQL配置
docker-compose exec db psql -U cardverification -c "
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
SELECT pg_reload_conf();
"
```

## 📈 监控和维护

### 1. 健康检查
```bash
# 检查所有服务健康状态
docker-compose ps

# 应用健康检查
curl http://localhost:8000/api/v1/health/

# 数据库健康检查
docker-compose exec db pg_isready
```

### 2. 日志管理
```bash
# 查看实时日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f web

# 清理日志
docker system prune -f
```

### 3. 数据备份
```bash
# 数据库备份
docker-compose exec db pg_dump -U cardverification cardverification > backup.sql

# 媒体文件备份
docker cp cardverification_web:/app/media ./media_backup

# 完整备份脚本
./docker/scripts/backup.sh
```

### 4. 更新部署
```bash
# 拉取最新代码
git pull origin main

# 重新构建并部署
docker-compose build
docker-compose up -d

# 运行数据库迁移
docker-compose exec web python manage.py migrate
```

## 🔒 安全配置

### 1. 生产环境安全检查清单
- [ ] 修改默认密码和密钥
- [ ] 配置HTTPS证书
- [ ] 限制数据库访问
- [ ] 启用防火墙规则
- [ ] 定期更新镜像
- [ ] 配置日志监控

### 2. SSL/TLS配置
```bash
# 生成自签名证书（测试用）
mkdir -p docker/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/nginx/ssl/key.pem \
  -out docker/nginx/ssl/cert.pem

# 启用HTTPS
# 编辑 docker/nginx/default.conf 取消HTTPS配置注释
```

### 3. 网络安全
```bash
# 创建自定义网络
docker network create cardverification_secure

# 限制容器间通信
# 编辑 docker-compose.yml 网络配置
```

## 📞 技术支持

如果遇到部署问题，请：

1. 检查系统要求和Docker版本
2. 查看详细错误日志
3. 参考故障排除章节
4. 提交Issue并附上相关日志

---

**注意：** 生产环境部署前请务必修改所有默认密码和配置！
