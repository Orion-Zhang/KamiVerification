# -*- coding: utf-8 -*-
"""
API混入类和装饰器
================

提供API开发中常用的混入类和装饰器，包括：
1. 请求验证和解析
2. 响应格式化
3. 错误处理
4. 日志记录
5. 性能监控

作者：Augment Agent
日期：2024
"""

import json
import time
import logging
from functools import wraps
from django.utils import timezone
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from .error_codes import ApiResponse, ApiErrorCode, get_http_status
from .models import ApiKey, ApiCallLog

logger = logging.getLogger(__name__)


class ApiRequestMixin:
    """API请求处理混入类"""
    
    def parse_request_data(self, request):
        """解析请求数据"""
        try:
            if request.content_type == 'application/json':
                if hasattr(request, 'body') and request.body:
                    return json.loads(request.body)
                else:
                    return {}
            else:
                return dict(request.POST)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON解析失败: {e}")
            raise ValueError("无效的JSON格式")
        except Exception as e:
            logger.error(f"请求数据解析失败: {e}")
            raise ValueError("请求数据解析失败")
    
    def validate_required_params(self, data, required_params):
        """验证必要参数"""
        missing_params = []
        for param in required_params:
            if not data.get(param):
                missing_params.append(param)
        
        if missing_params:
            return ApiResponse.missing_parameters(missing_params)
        return None
    
    def get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # 取第一个IP地址
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip
    
    def get_user_agent(self, request):
        """获取用户代理"""
        return request.META.get('HTTP_USER_AGENT', '')[:500]  # 限制长度


class ApiResponseMixin:
    """API响应处理混入类"""
    
    def success_response(self, data=None, message="操作成功"):
        """返回成功响应"""
        response_data = ApiResponse.success(data, message)
        return Response(response_data, status=get_http_status(response_data['code']))
    
    def error_response(self, error_code, message=None, data=None):
        """返回错误响应"""
        response_data = ApiResponse.error(error_code, message, data)
        return Response(response_data, status=get_http_status(response_data['code']))


class ApiLoggingMixin:
    """API日志记录混入类"""
    
    def log_api_call(self, api_key_obj, request, response_code, start_time, success, error_message='', endpoint=None):
        """记录API调用日志"""
        try:
            response_time = (timezone.now() - start_time).total_seconds() * 1000
            
            # 只有当api_key_obj不为None时才记录到数据库
            if api_key_obj is not None:
                ApiCallLog.objects.create(
                    api_key=api_key_obj,
                    endpoint=endpoint or request.path,
                    method=request.method,
                    ip_address=self.get_client_ip(request),
                    user_agent=self.get_user_agent(request),
                    response_code=response_code,
                    response_time=response_time,
                    success=success,
                    error_message=error_message[:1000]  # 限制错误消息长度
                )
            
            # 记录到日志文件
            log_level = logging.INFO if success else logging.WARNING
            logger.log(log_level, 
                f"API调用 - 端点:{endpoint or request.path} "
                f"方法:{request.method} IP:{self.get_client_ip(request)} "
                f"状态码:{response_code} 响应时间:{response_time:.2f}ms "
                f"成功:{success} 错误:{error_message}")
                
        except Exception as e:
            logger.error(f"记录API调用日志失败: {e}")


class ApiKeyValidationMixin:
    """API密钥验证混入类"""
    
    def validate_api_key(self, api_key):
        """验证API密钥"""
        if not api_key:
            return None, ApiResponse.missing_parameters(['api_key'])
        
        try:
            api_key_obj = ApiKey.objects.select_related('created_by').get(
                key=api_key, 
                is_active=True
            )
            
            # 检查频率限制（可以在这里添加Redis缓存实现）
            # TODO: 实现频率限制逻辑
            
            return api_key_obj, None
            
        except ApiKey.DoesNotExist:
            return None, ApiResponse.invalid_api_key()


class BaseApiView(APIView, ApiRequestMixin, ApiResponseMixin, ApiLoggingMixin, ApiKeyValidationMixin):
    """基础API视图类"""
    
    permission_classes = []  # 允许未认证访问
    authentication_classes = []  # 不需要认证
    
    def dispatch(self, request, *args, **kwargs):
        """重写dispatch方法，添加通用处理逻辑"""
        self.start_time = timezone.now()
        
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"API请求处理异常: {e}", exc_info=True)
            response_data = ApiResponse.system_error(f"系统内部错误")
            self.log_api_call(None, request, 500, self.start_time, False, str(e))
            return Response(response_data, status=get_http_status(response_data['code']))
    
    def handle_exception(self, exc):
        """统一异常处理"""
        logger.error(f"API异常: {exc}", exc_info=True)
        
        if isinstance(exc, ValueError):
            response_data = ApiResponse.error(ApiErrorCode.CARD_ERROR, str(exc))
        else:
            response_data = ApiResponse.system_error("系统内部错误")
        
        self.log_api_call(None, self.request, 500, self.start_time, False, str(exc))
        return Response(response_data, status=get_http_status(response_data['code']))


def api_monitor(func):
    """API性能监控装饰器"""
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        start_time = time.time()
        
        try:
            response = func(self, request, *args, **kwargs)
            
            # 记录性能指标
            duration = (time.time() - start_time) * 1000
            if duration > 1000:  # 超过1秒的请求记录警告
                logger.warning(f"慢API请求: {request.path} 耗时 {duration:.2f}ms")
            
            return response
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"API请求失败: {request.path} 耗时 {duration:.2f}ms 错误: {e}")
            raise
    
    return wrapper


def rate_limit(max_requests=60, window_seconds=60):
    """频率限制装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            # TODO: 实现基于Redis的频率限制
            # 当前简单实现，生产环境建议使用Redis
            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator


def require_api_key(func):
    """要求API密钥的装饰器"""
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        try:
            data = self.parse_request_data(request)
        except ValueError as e:
            return self.error_response(ApiErrorCode.CARD_ERROR, str(e))
        
        api_key = data.get('api_key')
        api_key_obj, error_response = self.validate_api_key(api_key)
        
        if error_response:
            self.log_api_call(None, request, 
                get_http_status(error_response['code']), 
                self.start_time, False, error_response['message'])
            return Response(error_response, status=get_http_status(error_response['code']))
        
        # 将API密钥对象添加到请求中
        request.api_key_obj = api_key_obj
        request.parsed_data = data
        
        return func(self, request, *args, **kwargs)
    
    return wrapper
