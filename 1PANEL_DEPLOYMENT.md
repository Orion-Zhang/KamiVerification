# 🚀 CardVerification 1Panel 部署指南

本指南专为使用 1Panel + OpenResty 环境部署 CardVerification 项目而设计。

## 📋 部署架构

```
Internet → 1Panel OpenResty (kami.killua.tech:443) → Container (127.0.0.1:8000)
                    ↓
            [PostgreSQL Container] + [Redis Container]
```

## 🔧 部署步骤

### 1. 服务器准备

确保您的服务器已安装：
- 1Panel 管理面板
- Docker 和 Docker Compose
- Git

### 2. 项目部署

```bash
# 1. 克隆项目到服务器
git clone <your-repo-url> /opt/cardverification
cd /opt/cardverification

# 2. 复制环境配置
cp .env.1panel.example .env

# 3. 编辑环境配置
nano .env
```

### 3. 环境配置

编辑 `.env` 文件，重点配置以下参数：

```bash
# 基础配置
DEBUG=False
SECRET_KEY=your-super-secure-secret-key-here
ALLOWED_HOSTS=127.0.0.1,localhost,kami.killua.tech

# 数据库配置
POSTGRES_DB=cardverification_prod
POSTGRES_USER=cardverification_user
POSTGRES_PASSWORD=your-secure-password

# 安全配置
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
```

### 4. 执行部署

```bash
# 设置执行权限
chmod +x deploy_1panel.sh manage_1panel.sh

# 执行部署
./deploy_1panel.sh
```

### 5. 1Panel 配置

#### 5.1 创建网站

在 1Panel 管理面板中：

1. **网站管理** → **创建网站**
2. **域名**: `kami.killua.tech`
3. **类型**: 反向代理
4. **代理地址**: `http://127.0.0.1:8000`

#### 5.2 SSL 证书配置

1. **SSL** → **申请证书**
2. 选择 Let's Encrypt 或上传自有证书
3. 启用 **强制 HTTPS**

#### 5.3 反向代理配置

在网站配置中添加以下反向代理规则：

```nginx
# 静态文件代理
location /static/ {
    proxy_pass http://127.0.0.1:8000/static/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # 缓存设置
    expires 30d;
    add_header Cache-Control "public, immutable";
}

# 媒体文件代理
location /media/ {
    proxy_pass http://127.0.0.1:8000/media/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # 缓存设置
    expires 7d;
    add_header Cache-Control "public";
}

# 应用代理
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # 超时设置
    proxy_connect_timeout 30s;
    proxy_send_timeout 30s;
    proxy_read_timeout 30s;
    
    # 缓冲设置
    proxy_buffering on;
    proxy_buffer_size 4k;
    proxy_buffers 8 4k;
}
```

## 📊 管理和维护

### 日常管理命令

```bash
# 查看状态
./manage_1panel.sh status

# 查看日志
./manage_1panel.sh logs

# 重启服务
./manage_1panel.sh restart

# 备份数据
./manage_1panel.sh backup

# 健康检查
./manage_1panel.sh health

# 显示1Panel配置信息
./manage_1panel.sh 1panel-info
```

### 容器管理

在 1Panel 面板中：

1. **容器管理** → 查看 CardVerification 相关容器
2. 监控容器资源使用情况
3. 查看容器日志
4. 管理容器生命周期

## 🔍 故障排除

### 常见问题

#### 1. 应用无法访问

```bash
# 检查容器状态
./manage_1panel.sh status

# 检查应用健康
curl http://127.0.0.1:8000/api/v1/health/

# 查看应用日志
./manage_1panel.sh logs
```

#### 2. 静态文件404

```bash
# 重新收集静态文件
./manage_1panel.sh collectstatic

# 检查静态文件目录
ls -la staticfiles/
```

#### 3. 数据库连接失败

```bash
# 检查数据库容器
docker-compose -f docker-compose.1panel.yml exec db pg_isready

# 查看数据库日志
docker-compose -f docker-compose.1panel.yml logs db
```

### 性能优化

#### 1. 容器资源限制

在 1Panel 中为容器设置合适的资源限制：

- **内存限制**: 512MB - 1GB
- **CPU限制**: 0.5 - 1.0 核心

#### 2. 数据库优化

```bash
# 进入数据库容器
./manage_1panel.sh dbshell

# 执行性能优化SQL
ANALYZE;
REINDEX DATABASE cardverification_prod;
```

## 📈 监控和告警

### 1Panel 监控配置

1. **监控** → **容器监控**
2. 设置资源使用告警阈值
3. 配置邮件/微信通知

### 应用监控

```bash
# 定期健康检查
*/5 * * * * /opt/cardverification/manage_1panel.sh health

# 定期备份
0 2 * * * /opt/cardverification/manage_1panel.sh backup
```

## 🔄 更新流程

```bash
# 1. 备份数据
./manage_1panel.sh backup

# 2. 更新代码
git pull origin main

# 3. 更新应用
./manage_1panel.sh update

# 4. 验证部署
./manage_1panel.sh health
```

## 📞 技术支持

### 访问地址

- **主页**: https://kami.killua.tech
- **管理后台**: https://kami.killua.tech/admin/
- **API文档**: https://kami.killua.tech/swagger/

### 日志位置

- **应用日志**: 通过Docker容器日志查看 `docker-compose logs web`
- **1Panel日志**: 通过1Panel面板查看
- **容器日志**: `docker-compose logs`

---

**🎉 恭喜！您的 CardVerification 系统已成功部署到 1Panel 环境！**
