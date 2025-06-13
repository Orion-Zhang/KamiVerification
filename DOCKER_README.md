# 卡片验证系统 Docker 生产环境部署

## 快速部署

### 1. 配置环境变量

编辑 `.env` 文件：

```bash
DEBUG=0
SECRET_KEY=your-super-secret-key-change-this-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
```

### 2. 构建并启动

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 3. 访问应用

- 应用地址: http://localhost:8000
- 管理后台: http://localhost:8000/admin
- 默认管理员: admin/admin123

## 管理命令

```bash
# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看运行状态
docker-compose ps

# 进入容器
docker-compose exec web bash

# 查看日志
docker-compose logs web
```

## 数据备份

```bash
# 备份数据库文件
docker-compose exec web cp /app/db.sqlite3 /app/media/backup_$(date +%Y%m%d).sqlite3

# 备份媒体文件
docker cp cardverification_prod:/app/media ./backup_media
```

## 注意事项

1. **生产环境安全**：
   - 修改 `.env` 文件中的 `SECRET_KEY`
   - 设置正确的 `ALLOWED_HOSTS`
   - 定期备份数据

2. **域名配置**：
   - 将 `your-domain.com` 替换为实际域名
   - 配置反向代理（如 Nginx）

3. **SSL 证书**：
   - 建议使用 HTTPS
   - 可以配置 Let's Encrypt 证书
