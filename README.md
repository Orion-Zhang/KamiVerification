# 🎯 Killua 卡密验证系统

[![Django](https://img.shields.io/badge/Django-5.2.3-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![DRF](https://img.shields.io/badge/DRF-3.16.0-orange.svg)](https://www.django-rest-framework.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![API](https://img.shields.io/badge/API-RESTful-red.svg)](#api-文档)

一个基于 Django 的现代化在线卡密验证系统，提供完整的卡密管理、用户管理、API接口和数据统计功能。

## 📋 目录

- [项目概述](#-项目概述)
- [功能特性](#-功能特性)
- [技术栈](#-技术栈)
- [快速开始](#-快速开始)
- [API 文档](#-api-文档)
- [系统架构](#-系统架构)
- [安全特性](#-安全特性)
- [部署指南](#-部署指南)
- [贡献指南](#-贡献指南)

## 🚀 项目概述

本系统为软件产品提供在线卡密验证服务，采用现代化的 Django 框架开发。用户通过管理员获取卡密，在本地软件中通过调用 RESTful API 实现授权验证。系统提供强大的后台管理功能，包括卡密生成、设备绑定、使用记录、数据统计等。

### ✨ 主要特性

- 🔐 **安全可靠**: SHA1加密存储，设备绑定防护，API密钥认证
- 🎨 **现代界面**: Bootstrap 5 响应式设计，支持暗色模式
- 📊 **数据可视化**: Chart.js 图表展示，实时统计分析
- 🔑 **API支持**: RESTful API 接口，Swagger 文档
- 📱 **多设备支持**: 灵活的设备绑定机制
- 📈 **统计分析**: 完整的数据统计和趋势分析
- 🌐 **国际化**: 完全中文化界面
- 🔧 **易于部署**: 详细部署文档和配置指南

## 🎯 功能特性

### 👥 用户管理系统

- ✅ **角色权限管理**: 超级管理员/普通管理员分级权限
- ✅ **审批机制**: 新用户注册需超级管理员审批
- ✅ **状态管理**: 待审批/已审批/已拒绝状态控制
- ✅ **登录安全**: 登录日志记录和安全监控
- ✅ **个人资料**: 完整的个人信息管理功能

### 🎫 卡密管理功能

- ✅ **多种类型**: 支持时间卡和次数卡两种类型
- ✅ **批量操作**: 单个创建和批量生成（支持自定义数量）
- ✅ **状态控制**: 启用/禁用/过期/用完状态管理
- ✅ **设备绑定**: 灵活的设备绑定与解绑功能
- ✅ **数据导出**: Excel 导出功能（支持筛选导出）
- ✅ **高级搜索**: 多字段搜索和智能分页
- ✅ **使用记录**: 详细的卡密使用历史追踪

### 🔌 API 验证系统

- ✅ **RESTful 设计**: 标准化的 API 接口设计
- ✅ **多密钥支持**: 支持多个 API 密钥管理
- ✅ **频率限制**: 防止 API 滥用的调用限制
- ✅ **设备验证**: 强大的设备绑定验证机制
- ✅ **调用日志**: 详细的调用记录和错误追踪
- ✅ **健康检查**: API 服务健康状态监控
- ✅ **文档支持**: 完整的 Swagger API 文档

### 📊 数据统计面板

- ✅ **实时监控**: 实时数据统计和系统监控
- ✅ **图表展示**: Chart.js 驱动的数据可视化
- ✅ **趋势分析**: 验证趋势和使用模式分析
- ✅ **性能监控**: API 调用性能和响应时间分析
- ✅ **系统状态**: 全面的系统健康状态检查

## 🛠 技术栈

### 后端技术
- **Django 5.2.3** - 现代化 Web 框架
- **Django REST Framework 3.16.0** - API 构建框架
- **SQLite** - 轻量级数据库（支持 MySQL/PostgreSQL）
- **pandas 2.3.0** - 数据处理和分析
- **openpyxl 3.1.5** - Excel 文件处理

### 前端技术
- **Bootstrap 5.3** - 响应式 UI 框架
- **Chart.js** - 数据可视化图表库
- **Font Awesome 6.0** - 图标库
- **JavaScript ES6+** - 现代化前端交互
- **CSS3** - 现代化样式设计

### API 和文档
- **drf-yasg 1.21.10** - Swagger API 文档生成
- **RESTful API** - 标准化接口设计
- **JSON** - 数据交换格式

### 开发工具
- **Python 3.8+** - 编程语言
- **pip** - 包管理工具
- **Git** - 版本控制

## 🚀 快速开始

### 环境要求
- Python 3.8 或更高版本
- pip 包管理器
- Git（可选）

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/your-username/CardVerification.git
   cd CardVerification
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv .venv

   # Windows
   .\.venv\Scripts\activate.ps1

   # Linux/Mac
   source .venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **数据库初始化**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **启动服务**
   ```bash
   python manage.py runserver
   ```

6. **访问系统**
   - 前端界面: http://127.0.0.1:8000/
   - 管理后台: http://127.0.0.1:8000/admin/
   - API 文档: http://127.0.0.1:8000/swagger/

## 📚 API 文档

### 主要接口

#### 卡密验证
```http
POST /api/v1/verify/
Content-Type: application/json

{
    "api_key": "your_api_key",
    "card_key": "card_key_to_verify",
    "device_id": "optional_device_id"
}
```

#### 卡密查询
```http
POST /api/v1/query/
Content-Type: application/json

{
    "api_key": "your_api_key",
    "card_key": "card_key_to_query"
}
```

#### 健康检查
```http
GET /api/v1/health/
```

### 错误码说明

| 错误码 | 说明 | HTTP状态码 |
|--------|------|------------|
| 0 | 成功 | 200 |
| 1 | 卡密相关错误 | 400 |
| 2 | API接口未启用 | 403 |
| 3 | 系统错误 | 500 |
| 4 | API密钥无效 | 401 |
| 5 | 卡密已被禁用 | 403 |

详细的 API 文档请访问: `/swagger/`

## 🏗 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端界面      │    │   API 接口      │    │   管理后台      │
│  (Bootstrap)    │    │  (DRF + Swagger)│    │  (Django Admin) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────┐
         │              Django 应用层                      │
         │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐│
         │  │accounts │ │  cards  │ │   api   │ │dashboard││
         │  └─────────┘ └─────────┘ └─────────┘ └─────────┘│
         └─────────────────────────────────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────┐
         │                数据层                           │
         │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐│
         │  │  用户   │ │  卡密   │ │ API密钥 │ │  日志   ││
         │  └─────────┘ └─────────┘ └─────────┘ └─────────┘│
         └─────────────────────────────────────────────────┘
```

## 🔒 安全特性

### 数据安全
- ✅ **卡密加密**: SHA1 哈希存储，原始卡密不保存
- ✅ **设备绑定**: 限制设备数量，防止卡密盗用
- ✅ **API 认证**: 密钥验证机制，防止未授权访问
- ✅ **频率限制**: 防止 API 滥用和暴力破解

### 系统安全
- ✅ **CSRF 保护**: Django 内置安全机制
- ✅ **SQL 注入防护**: ORM 查询防护
- ✅ **XSS 防护**: 模板自动转义
- ✅ **操作日志**: 完整的审计追踪

### 访问控制
- ✅ **角色权限**: 分级权限管理
- ✅ **审批机制**: 新用户审批流程
- ✅ **会话管理**: 安全的会话控制
- ✅ **IP 记录**: 访问 IP 地址记录

## 📁 项目结构

```
CardVerification/
├── CardVerification/          # 项目配置
│   ├── settings.py           # Django 设置
│   ├── urls.py              # 主路由配置
│   └── wsgi.py              # WSGI 配置
├── accounts/                 # 用户管理模块
│   ├── models.py            # 用户模型
│   ├── views.py             # 用户视图
│   └── admin.py             # 用户管理后台
├── cards/                    # 卡密管理模块
│   ├── models.py            # 卡密模型
│   ├── views.py             # 卡密视图
│   └── admin.py             # 卡密管理后台
├── api/                      # API 接口模块
│   ├── views.py             # API 视图
│   ├── serializers.py       # 序列化器
│   ├── error_codes.py       # 错误码定义
│   └── swagger.py           # API 文档配置
├── dashboard/                # 控制面板模块
│   ├── views.py             # 面板视图
│   └── models.py            # 面板模型
├── settings/                 # 系统设置模块
│   ├── models.py            # 设置模型
│   └── views.py             # 设置视图
├── templates/                # 模板文件
│   ├── base.html            # 基础模板
│   ├── accounts/            # 用户模板
│   ├── cards/               # 卡密模板
│   └── dashboard/           # 面板模板
├── static/                   # 静态文件
│   ├── css/                 # 样式文件
│   ├── js/                  # JavaScript 文件
│   └── fonts/               # 字体文件
├── requirements.txt          # 依赖包列表
├── manage.py                # Django 管理脚本
└── README.md                # 项目说明文档
```

## 🚀 部署指南

### 开发环境部署

1. **按照快速开始步骤安装**
2. **配置开发设置**
   ```python
   # settings.py
   DEBUG = True
   ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
   ```

### 生产环境部署

1. **环境配置**
   ```bash
   # 设置环境变量
   export DJANGO_SETTINGS_MODULE=CardVerification.settings
   export DEBUG=False
   export SECRET_KEY=your-secret-key
   ```

2. **数据库配置**
   ```python
   # 生产环境建议使用 PostgreSQL 或 MySQL
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'cardverification',
           'USER': 'your_user',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

3. **静态文件收集**
   ```bash
   python manage.py collectstatic
   ```

4. **使用 Gunicorn 部署**
   ```bash
   pip install gunicorn
   gunicorn CardVerification.wsgi:application
   ```

### Docker 部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "CardVerification.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 📊 功能演示

### 主要页面截图

1. **控制面板** - 实时数据统计和图表展示
2. **卡密管理** - 卡密列表、创建和批量操作
3. **API 管理** - API 密钥管理和调用统计
4. **用户管理** - 用户审批和权限管理

### API 使用示例

#### Python 示例
```python
import requests

# 卡密验证
response = requests.post('http://your-domain.com/api/v1/verify/', json={
    'api_key': 'your_api_key',
    'card_key': 'your_card_key',
    'device_id': 'device_123'
})

result = response.json()
if result['success']:
    print("验证成功:", result['data'])
else:
    print("验证失败:", result['message'])
```

#### JavaScript 示例
```javascript
// 卡密验证
fetch('/api/v1/verify/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        api_key: 'your_api_key',
        card_key: 'your_card_key',
        device_id: 'device_123'
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('验证成功:', data.data);
    } else {
        console.log('验证失败:', data.message);
    }
});
```

## 🤝 贡献指南

我们欢迎所有形式的贡献！请遵循以下步骤：

1. **Fork 项目**
2. **创建功能分支** (`git checkout -b feature/AmazingFeature`)
3. **提交更改** (`git commit -m 'Add some AmazingFeature'`)
4. **推送到分支** (`git push origin feature/AmazingFeature`)
5. **创建 Pull Request**

### 开发规范

- 遵循 PEP 8 Python 代码规范
- 添加适当的注释和文档
- 编写单元测试
- 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- **项目维护者**: Augment Agent
- **邮箱**: your-email@example.com
- **项目地址**: https://github.com/your-username/CardVerification
- **问题反馈**: https://github.com/your-username/CardVerification/issues

## 🙏 致谢

感谢以下开源项目的支持：

- [Django](https://www.djangoproject.com/) - Web 框架
- [Django REST Framework](https://www.django-rest-framework.org/) - API 框架
- [Bootstrap](https://getbootstrap.com/) - UI 框架
- [Chart.js](https://www.chartjs.org/) - 图表库
- [Font Awesome](https://fontawesome.com/) - 图标库

---

⭐ 如果这个项目对您有帮助，请给我们一个 Star！

