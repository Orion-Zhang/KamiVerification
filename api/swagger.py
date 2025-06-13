# -*- coding: utf-8 -*-
"""
API文档配置
==========

配置Swagger/OpenAPI文档生成。

作者：Augment Agent
日期：2024
"""

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# API文档基本信息
schema_view = get_schema_view(
    openapi.Info(
        title="Killua 卡密验证系统 API",
        default_version='v1',
        description="""
# Killua 卡密验证系统 API 文档

## 概述
本API提供卡密验证和查询功能，支持多种卡密类型和设备绑定机制。

## 认证方式
所有API请求都需要在请求体中包含有效的`api_key`参数。

## 错误码说明
| 错误码 | 说明 | HTTP状态码 | 处理建议 |
|--------|------|------------|----------|
| 0 | 成功 | 200 | 请求成功，可以正常处理返回的数据 |
| 1 | 卡密相关错误 | 400 | 检查卡密是否存在、有效或设备绑定 |
| 2 | API接口未启用 | 403 | 联系管理员启用API接口 |
| 3 | 系统错误 | 500 | 服务器内部错误，稍后重试 |
| 4 | API密钥无效 | 401 | 检查API密钥是否正确或已被禁用 |
| 5 | 卡密已被禁用 | 403 | 联系管理员处理禁用的卡密 |

## 卡密类型
- **时间卡 (time)**: 基于有效期的卡密
- **次数卡 (count)**: 基于使用次数的卡密

## 设备绑定
系统支持设备绑定功能，可以限制卡密在特定设备上使用。

## 频率限制
API调用受到频率限制，具体限制根据API密钥配置而定。

## 示例代码

### Python
```python
import requests

url = "https://your-domain.com/api/v1/verify/"
data = {
    "api_key": "your_api_key_here",
    "card_key": "your_card_key_here",
    "device_id": "optional_device_id"
}

response = requests.post(url, json=data)
result = response.json()

if result['success']:
    print("验证成功:", result['data'])
else:
    print("验证失败:", result['message'])
```

### JavaScript
```javascript
const response = await fetch('https://your-domain.com/api/v1/verify/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        api_key: 'your_api_key_here',
        card_key: 'your_card_key_here',
        device_id: 'optional_device_id'
    })
});

const result = await response.json();

if (result.success) {
    console.log('验证成功:', result.data);
} else {
    console.log('验证失败:', result.message);
}
```

### cURL
```bash
curl -X POST https://your-domain.com/api/v1/verify/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "api_key": "your_api_key_here",
    "card_key": "your_card_key_here",
    "device_id": "optional_device_id"
  }'
```

## 联系方式
如有问题，请联系系统管理员。
        """,
        terms_of_service="https://your-domain.com/terms/",
        contact=openapi.Contact(email="admin@your-domain.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    patterns=[
        # 只包含API端点，不包含管理页面
    ],
)

# 常用的响应示例
COMMON_RESPONSES = {
    400: openapi.Response(
        description="请求参数错误",
        examples={
            "application/json": {
                "code": 1,
                "success": False,
                "message": "缺少必要参数: card_key"
            }
        }
    ),
    401: openapi.Response(
        description="API密钥无效",
        examples={
            "application/json": {
                "code": 4,
                "success": False,
                "message": "API密钥无效或已被禁用"
            }
        }
    ),
    403: openapi.Response(
        description="访问被拒绝",
        examples={
            "application/json": {
                "code": 5,
                "success": False,
                "message": "卡密已被禁用"
            }
        }
    ),
    404: openapi.Response(
        description="资源不存在",
        examples={
            "application/json": {
                "code": 1,
                "success": False,
                "message": "卡密不存在"
            }
        }
    ),
    500: openapi.Response(
        description="服务器内部错误",
        examples={
            "application/json": {
                "code": 3,
                "success": False,
                "message": "系统内部错误"
            }
        }
    ),
}

# 常用的参数定义
COMMON_PARAMETERS = {
    'api_key': openapi.Parameter(
        'api_key',
        openapi.IN_FORM,
        description="API密钥，用于身份验证",
        type=openapi.TYPE_STRING,
        required=True,
        example="a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
    ),
    'card_key': openapi.Parameter(
        'card_key',
        openapi.IN_FORM,
        description="卡密",
        type=openapi.TYPE_STRING,
        required=True,
        example="CARD-KEY-123456"
    ),
    'device_id': openapi.Parameter(
        'device_id',
        openapi.IN_FORM,
        description="设备ID（可选），用于设备绑定",
        type=openapi.TYPE_STRING,
        required=False,
        example="DEVICE-001"
    ),
}

# 成功响应示例
SUCCESS_RESPONSE_EXAMPLES = {
    'verify_success': {
        "code": 0,
        "success": True,
        "message": "验证成功",
        "data": {
            "card_type": "time",
            "expire_date": "2024-12-31T23:59:59Z",
            "remaining_count": None,
            "device_binding": {
                "device_id": "DEVICE-001",
                "is_new_device": False
            }
        }
    },
    'query_success': {
        "code": 0,
        "success": True,
        "message": "查询成功",
        "data": {
            "card_info": {
                "card_type": "count",
                "status": "active",
                "expire_date": None,
                "total_count": 100,
                "used_count": 25,
                "remaining_count": 75,
                "first_used_at": "2024-01-01T10:00:00Z",
                "last_used_at": "2024-01-15T14:30:00Z",
                "allow_multi_device": True,
                "max_devices": 3,
                "is_expired": False
            },
            "device_bindings": [
                {
                    "device_id": "DEVICE-001",
                    "device_name": "User Device 1",
                    "ip_address": "192.168.1.100",
                    "first_bind_time": "2024-01-01T10:00:00Z",
                    "last_active_time": "2024-01-15T14:30:00Z"
                }
            ],
            "recent_logs": [
                {
                    "verification_time": "2024-01-15T14:30:00Z",
                    "ip_address": "192.168.1.100",
                    "success": True,
                    "error_message": ""
                }
            ]
        }
    }
}
