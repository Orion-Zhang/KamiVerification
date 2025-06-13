# 🚀 CardVerification 生产环境部署指南

本指南详细说明了 CardVerification 项目的生产环境部署配置和优化。

## 📋 配置优化总览

### ✅ 已完成的优化

1. **数据库配置优化**
   - 增加连接复用时间到5分钟
   - 添加连接健康检查
   - 配置SSL连接支持
   - 优化SQLite超时设置

2. **缓存系统配置**
   - 添加Redis缓存支持
   - 配置会话缓存
   - 支持缓存中间件

3. **安全配置完善**
   - HTTPS强制重定向
   - HSTS安全头
   - Cookie安全配置
   - 内容安全策略

4. **日志系统配置**
   - 分级日志记录
   - 日志轮转配置
   - 模块化日志处理

5. **Docker配置优化**
   - 多阶段构建
   - 健康检查
   - 安全用户配置

## 🔧 部署步骤

### 1. 环境准备

```bash
# 克隆项目
git clone <your-repo-url>
cd CardVerification

# 复制环境配置文件
cp .env.production.example .env.production

# 编辑生产环境配置
nano .env.production
```

### 2. 配置环境变量

编辑 `.env.production` 文件，设置以下关键配置：

```bash
# 基础配置
DEBUG=False
SECRET_KEY=your-super-secure-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# 数据库配置
POSTGRES_DB=cardverification_prod
POSTGRES_USER=cardverification_user
POSTGRES_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=5432

# Redis配置
REDIS_URL=redis://localhost:6379/1
USE_REDIS_SESSIONS=True

# 安全配置
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000

# 邮件配置
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 3. 部署方式选择

#### 方式一：Docker Compose 部署（推荐）

```bash
# 开发环境
./deploy.sh dev

# 生产环境
./deploy.sh prod
```

#### 方式二：手动部署

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行迁移
python manage.py migrate

# 3. 收集静态文件
python manage.py collectstatic --noinput

# 4. 启动服务
gunicorn CardVerification.wsgi:application --bind 0.0.0.0:8000
```

## 📊 性能优化建议

### 1. 数据库优化

```sql
-- 添加常用索引
CREATE INDEX CONCURRENTLY idx_cards_status ON cards_card(status);
CREATE INDEX CONCURRENTLY idx_cards_created_at ON cards_card(created_at);
CREATE INDEX CONCURRENTLY idx_api_calls_created_at ON api_apicalllog(created_at);
```

### 2. 缓存策略

```python
# 在视图中使用缓存
from django.core.cache import cache

def get_statistics():
    stats = cache.get('dashboard_stats')
    if not stats:
        stats = calculate_statistics()
        cache.set('dashboard_stats', stats, 300)  # 5分钟缓存
    return stats
```

### 3. 静态文件优化

```nginx
# Nginx 配置
location /static/ {
    alias /app/staticfiles/;
    expires 30d;
    add_header Cache-Control "public, immutable";
    gzip_static on;
}
```

## 🔒 安全配置

### 1. SSL/TLS 配置

```bash
# 生成SSL证书 (Let's Encrypt)
certbot certonly --webroot -w /var/www/html -d yourdomain.com
```

### 2. 防火墙配置

```bash
# UFW 防火墙规则
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### 3. 定期安全更新

```bash
# 系统更新
apt update && apt upgrade -y

# Docker 镜像更新
docker-compose pull
docker-compose up -d
```

## 📈 监控和维护

### 1. 日志监控

```bash
# 查看应用日志
tail -f logs/django.log

# 查看错误日志
tail -f logs/django_error.log

# 查看API日志
tail -f logs/api.log
```

### 2. 性能监控

```bash
# 系统资源监控
./manage_prod.sh monitor

# 数据库性能
docker-compose exec db psql -U user -d db -c "SELECT * FROM pg_stat_activity;"
```

### 3. 备份策略

```bash
# 自动备份脚本
./manage_prod.sh backup

# 定时备份 (crontab)
0 2 * * * /path/to/manage_prod.sh backup
```

## 🚨 故障排除

### 1. 常见问题

**问题：服务无法启动**
```bash
# 检查日志
docker-compose logs web

# 检查配置
docker-compose config
```

**问题：数据库连接失败**
```bash
# 检查数据库状态
docker-compose exec db pg_isready

# 检查网络连接
docker-compose exec web ping db
```

**问题：静态文件404**
```bash
# 重新收集静态文件
docker-compose exec web python manage.py collectstatic --noinput

# 检查Nginx配置
docker-compose exec nginx nginx -t
```

### 2. 性能问题

**问题：响应缓慢**
- 检查数据库查询性能
- 启用缓存
- 优化数据库索引

**问题：内存使用过高**
- 调整Gunicorn工作进程数
- 优化数据库连接池
- 检查内存泄漏

## 📞 技术支持

如果遇到部署问题，请：

1. 检查日志文件
2. 查看本文档的故障排除部分
3. 提交Issue到项目仓库

## 🔄 更新流程

```bash
# 1. 备份数据
./manage_prod.sh backup

# 2. 更新代码
git pull origin main

# 3. 更新应用
./manage_prod.sh update

# 4. 验证部署
./manage_prod.sh status
```

---

**🎉 恭喜！您的 CardVerification 系统已经完成生产环境优化配置！**
