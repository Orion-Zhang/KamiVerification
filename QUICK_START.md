# 🚀 Killua 卡密验证系统 - 快速启动指南

[![Django](https://img.shields.io/badge/Django-5.2.3-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)](#)

本指南将帮助您在 5 分钟内快速启动 Killua 卡密验证系统。

## 📋 前置要求

### 系统要求
- **Python**: 3.8 或更高版本
- **内存**: 最少 512MB RAM
- **存储**: 最少 100MB 可用空间
- **网络**: 互联网连接（用于安装依赖）

### 开发工具
- **pip**: Python 包管理器
- **Git**: 版本控制工具（可选）
- **代码编辑器**: VS Code、PyCharm 等（推荐）

## ⚡ 一键启动脚本

### Windows 用户
```powershell
# 下载并运行一键启动脚本
curl -o quick_start.ps1 https://raw.githubusercontent.com/your-repo/CardVerification/main/scripts/quick_start.ps1
.\quick_start.ps1
```

### Linux/Mac 用户
```bash
# 下载并运行一键启动脚本
curl -o quick_start.sh https://raw.githubusercontent.com/your-repo/CardVerification/main/scripts/quick_start.sh
chmod +x quick_start.sh
./quick_start.sh
```

## 🛠️ 手动安装步骤

### 1. 获取项目代码

#### 方式一：Git 克隆（推荐）
```bash
git clone https://github.com/your-username/CardVerification.git
cd CardVerification
```

#### 方式二：下载压缩包
1. 访问项目 GitHub 页面
2. 点击 "Code" -> "Download ZIP"
3. 解压到本地目录

### 2. 创建虚拟环境
```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat

# Linux/Mac
source .venv/bin/activate
```

### 3. 安装项目依赖
```bash
# 安装所有依赖
pip install -r requirements.txt

# 验证安装
pip list
```

**依赖包说明**：
- `Django==5.2.3` - Web 框架核心
- `djangorestframework==3.16.0` - API 构建框架
- `pandas==2.3.0` - 数据处理
- `openpyxl==3.1.5` - Excel 文件处理
- `drf-yasg==1.21.10` - API 文档生成

### 4. 数据库初始化
```bash
# 创建数据库迁移文件
python manage.py makemigrations

# 执行数据库迁移
python manage.py migrate

# 创建超级管理员账户
python manage.py createsuperuser
```

**超级管理员信息**：
- 用户名：建议使用 `admin`
- 邮箱：输入您的邮箱地址
- 密码：设置强密码（至少8位）

### 5. 启动开发服务器
```bash
# 启动服务器
python manage.py runserver

# 指定端口启动（可选）
python manage.py runserver 8080
```

## 🌐 访问系统

### 🎯 主要访问地址

| 功能 | 地址 | 说明 |
|------|------|------|
| 🏠 **主页** | http://127.0.0.1:8000/ | 系统介绍和 API 文档 |
| 🔧 **管理后台** | http://127.0.0.1:8000/admin/ | Django 原生管理界面 |
| 📊 **控制面板** | http://127.0.0.1:8000/dashboard/ | 现代化管理界面 |
| 🎫 **卡密管理** | http://127.0.0.1:8000/cards/ | 卡密创建和管理 |
| 🔑 **API管理** | http://127.0.0.1:8000/api/keys/ | API 密钥管理 |
| 📚 **API文档** | http://127.0.0.1:8000/swagger/ | Swagger 接口文档 |
| ⚕️ **健康检查** | http://127.0.0.1:8000/api/v1/health/ | 系统状态检查 |

## 🔑 首次登录指南

### 1. 管理后台登录
1. 访问：http://127.0.0.1:8000/admin/
2. 输入超级管理员用户名和密码
3. 点击"登录"进入 Django 管理界面

### 2. 前端控制面板登录
1. 访问：http://127.0.0.1:8000/dashboard/
2. 使用相同的超级管理员账户登录
3. 进入现代化的管理界面

### 3. 首次登录检查清单
- [ ] 成功登录管理后台
- [ ] 成功登录前端控制面板
- [ ] 查看系统统计数据
- [ ] 访问 API 文档页面

## ⚡ 快速配置

### 1. 创建第一个 API 密钥

#### 方式一：通过 Web 界面（推荐）
1. 登录控制面板：http://127.0.0.1:8000/dashboard/
2. 点击"API 管理" -> "创建 API 密钥"
3. 填写密钥名称和调用限制
4. 点击"创建"并保存生成的密钥

#### 方式二：通过命令行
```bash
# 进入 Django shell
python manage.py shell

# 执行以下 Python 代码
from api.models import ApiKey
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username='admin')  # 替换为您的用户名

api_key = ApiKey.objects.create(
    name='测试密钥',
    created_by=user,
    rate_limit=1000  # 每小时1000次调用限制
)

print(f'✅ API密钥创建成功: {api_key.key}')
print(f'📝 请妥善保存此密钥，它不会再次显示')
```

### 2. 创建测试卡密

#### 方式一：通过 Web 界面（推荐）
1. 访问：http://127.0.0.1:8000/cards/
2. 点击"创建卡密"
3. 选择卡密类型（时间卡/次数卡）
4. 设置相关参数
5. 点击"创建"

#### 方式二：批量生成
1. 访问：http://127.0.0.1:8000/cards/batch-create/
2. 选择卡密类型和数量
3. 设置参数
4. 点击"批量生成"

#### 方式三：通过命令行
```bash
# 继续在 Django shell 中执行
from cards.models import Card
import secrets
from datetime import datetime, timedelta

# 创建时间卡（30天有效期）
time_card = Card.objects.create(
    card_key=secrets.token_urlsafe(16),
    card_type='time',
    valid_days=30,
    created_by=user,
    note='测试时间卡'
)
print(f'⏰ 时间卡创建成功: {time_card.card_key}')

# 创建次数卡（100次使用）
count_card = Card.objects.create(
    card_key=secrets.token_urlsafe(16),
    card_type='count',
    total_count=100,
    created_by=user,
    note='测试次数卡'
)
print(f'🔢 次数卡创建成功: {count_card.card_key}')
```

## 🧪 API 测试

### 1. 健康检查测试
```bash
# 测试系统状态
curl -X GET http://127.0.0.1:8000/api/v1/health/
```

**预期响应**：
```json
{
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00Z",
    "version": "1.0.0",
    "database": "connected",
    "stats": {
        "total_api_keys": 1,
        "total_cards": 2,
        "active_api_keys": 1
    }
}
```

### 2. 卡密验证测试

#### 使用 curl
```bash
# 替换为您的实际 API 密钥和卡密
curl -X POST http://127.0.0.1:8000/api/v1/verify/ \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your_api_key_here",
    "card_key": "your_card_key_here",
    "device_id": "test_device_001"
  }'
```

#### 使用 Python
```python
import requests

# 卡密验证测试
response = requests.post('http://127.0.0.1:8000/api/v1/verify/', json={
    'api_key': 'your_api_key_here',  # 替换为实际密钥
    'card_key': 'your_card_key_here',  # 替换为实际卡密
    'device_id': 'test_device_001'
})

result = response.json()
print(f"状态码: {response.status_code}")
print(f"响应内容: {result}")

if result.get('success'):
    print("✅ 验证成功!")
    print(f"卡密类型: {result['data']['card_type']}")
else:
    print("❌ 验证失败!")
    print(f"错误信息: {result['message']}")
```

### 3. 卡密查询测试
```bash
# 查询卡密信息
curl -X POST http://127.0.0.1:8000/api/v1/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your_api_key_here",
    "card_key": "your_card_key_here"
  }'
```

**预期响应**：
```json
{
    "code": 0,
    "success": true,
    "message": "查询成功",
    "data": {
        "card_type": "time",
        "status": "active",
        "expire_date": "2024-12-31T23:59:59Z",
        "total_count": null,
        "used_count": 0,
        "remaining_count": null,
        "first_used_at": null,
        "last_used_at": null,
        "is_expired": false,
        "allow_multi_device": false,
        "max_devices": 1
    }
}
```

## 📊 功能导览

### 🎯 主要功能模块

| 模块 | 路径 | 功能描述 |
|------|------|----------|
| 📊 **控制面板** | `/dashboard/` | 系统统计概览、实时数据图表、快速操作入口 |
| 🎫 **卡密管理** | `/cards/` | 卡密列表搜索、创建单个卡密、批量生成、Excel导出 |
| 🔑 **API管理** | `/api/keys/` | API密钥管理、调用记录查看、使用统计分析 |
| 👤 **用户管理** | `/accounts/` | 个人资料修改、账户状态查看、密码修改 |
| ⚙️ **系统设置** | `/settings/` | 系统配置、功能开关、联系信息设置 |

### 🔧 管理功能

- **用户审批**: 超级管理员可以审批新注册的管理员
- **权限控制**: 基于角色的访问控制
- **数据导出**: 支持 Excel 格式的数据导出
- **日志记录**: 完整的操作日志和访问记录
- **API 文档**: 自动生成的 Swagger API 文档

## 🔍 故障排除

### 🚨 常见问题及解决方案

#### 1. **虚拟环境问题**
```bash
# 检查虚拟环境是否激活
which python  # Linux/Mac
where python   # Windows

# 重新激活虚拟环境
# Windows
.\.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate
```

#### 2. **依赖包问题**
```bash
# 检查已安装的包
pip list

# 重新安装依赖
pip install -r requirements.txt --upgrade

# 清理缓存重新安装
pip cache purge
pip install -r requirements.txt
```

#### 3. **数据库问题**
```bash
# 检查数据库文件
ls -la db.sqlite3

# 重置数据库
rm db.sqlite3
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

#### 4. **端口占用问题**
```bash
# 检查端口占用
netstat -an | grep 8000  # Linux/Mac
netstat -an | findstr 8000  # Windows

# 使用其他端口
python manage.py runserver 8080
python manage.py runserver 0.0.0.0:8000  # 允许外部访问
```

#### 5. **静态文件问题**
```bash
# 收集静态文件
python manage.py collectstatic --noinput

# 清理静态文件缓存
rm -rf static/  # 删除静态文件目录
python manage.py collectstatic
```

### 🔧 调试技巧

#### 启用调试模式
```python
# 在 settings.py 中设置
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

#### 检查系统状态
```bash
# 运行系统检查
python manage.py check

# 检查数据库连接
python manage.py dbshell

# 查看迁移状态
python manage.py showmigrations
```

## 📝 开发建议

### 🔄 开发流程

1. **代码修改后**
   - 保存文件后 Django 会自动重载
   - 检查控制台是否有错误信息
   - 刷新浏览器查看效果

2. **模型修改后**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **静态文件修改后**
   - 硬刷新浏览器 (Ctrl+Shift+R)
   - 检查浏览器开发者工具的网络选项卡
   - 必要时运行 `collectstatic`

### 🛠 开发工具推荐

- **代码编辑器**: VS Code + Python 扩展
- **API 测试**: Postman 或 Insomnia
- **数据库管理**: DB Browser for SQLite
- **版本控制**: Git + GitHub Desktop

## 🎯 下一步操作

### 📚 学习路径

1. **熟悉系统** (30分钟)
   - [ ] 浏览所有功能模块
   - [ ] 创建测试数据
   - [ ] 查看 API 文档

2. **API 集成** (1小时)
   - [ ] 测试验证接口
   - [ ] 测试查询接口
   - [ ] 集成到您的应用

3. **自定义配置** (30分钟)
   - [ ] 修改系统设置
   - [ ] 配置联系信息
   - [ ] 调整功能开关

4. **生产部署** (根据需要)
   - [ ] 配置生产环境
   - [ ] 设置域名和 HTTPS
   - [ ] 配置数据库备份

### 🔗 有用链接

- **项目文档**: [README.md](README.md)
- **API 文档**: http://127.0.0.1:8000/swagger/
- **Django 官方文档**: https://docs.djangoproject.com/
- **DRF 文档**: https://www.django-rest-framework.org/

## 📞 获取帮助

### 🆘 遇到问题时

1. **检查日志**
   - 查看控制台输出
   - 检查 Django 错误页面
   - 查看浏览器开发者工具

2. **查阅文档**
   - 项目 README
   - API 文档
   - Django 官方文档

3. **社区支持**
   - GitHub Issues
   - Django 社区论坛
   - Stack Overflow

### 📧 联系方式

- **项目维护者**: Augment Agent
- **技术支持**: 通过 GitHub Issues 提交问题
- **功能建议**: 欢迎提交 Pull Request

---

## 🎉 恭喜！

**您已成功启动 Killua 卡密验证系统！**

现在您可以：
- ✅ 创建和管理卡密
- ✅ 配置 API 密钥
- ✅ 集成验证接口
- ✅ 监控系统状态

**祝您使用愉快！** 🚀
