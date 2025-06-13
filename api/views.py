from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db.models import Q
from django import forms
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import hashlib
import json
import logging

from .models import ApiKey, ApiCallLog
from cards.models import Card, DeviceBinding, VerificationLog
from accounts.mixins import ApprovedUserRequiredMixin
from .error_codes import ApiResponse, ApiErrorCode, get_http_status
from .mixins import BaseApiView, api_monitor, require_api_key
from .serializers import (
    CardVerifyRequestSerializer, CardVerifyResponseSerializer,
    CardQueryRequestSerializer, CardQueryResponseSerializer,
    ErrorResponseSerializer
)
from .services import CardVerificationService, CardQueryService, LoggingService

logger = logging.getLogger(__name__)


class ApiKeyForm(forms.ModelForm):
    """API密钥表单"""
    class Meta:
        model = ApiKey
        fields = ['name', 'rate_limit']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'rate_limit': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class VerifyCardView(BaseApiView):
    """
    卡密验证API

    验证卡密的有效性，支持设备绑定功能。
    """

    @swagger_auto_schema(
        operation_description="验证卡密",
        request_body=CardVerifyRequestSerializer,
        responses={
            200: CardVerifyResponseSerializer,
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        tags=['卡密验证']
    )
    @api_monitor
    @require_api_key
    def post(self, request):
        """验证卡密"""
        try:
            # 验证请求数据
            serializer = CardVerifyRequestSerializer(data=request.parsed_data)
            if not serializer.is_valid():
                error_msg = '; '.join([f"{k}: {', '.join(v)}" for k, v in serializer.errors.items()])
                response_data = ApiResponse.error(ApiErrorCode.CARD_ERROR, f"参数验证失败: {error_msg}")
                self.log_api_call(request.api_key_obj, request, 400, self.start_time, False, error_msg)
                return Response(response_data, status=get_http_status(response_data['code']))

            validated_data = serializer.validated_data
            card_key = validated_data['card_key']
            device_id = validated_data.get('device_id')

            # 调用业务逻辑服务
            success, response_data, card = CardVerificationService.verify_card(
                request.api_key_obj, card_key, device_id, request
            )

            # 记录验证日志
            if card:
                LoggingService.log_verification(
                    card, request, validated_data['api_key'],
                    success, response_data.get('message', ''), None
                )

            # 记录API调用日志
            status_code = get_http_status(response_data['code'])
            self.log_api_call(
                request.api_key_obj, request, status_code,
                self.start_time, success, response_data.get('message', '')
            )

            return Response(response_data, status=status_code)

        except Exception as e:
            logger.error(f"卡密验证异常: {e}", exc_info=True)
            response_data = ApiResponse.system_error("验证过程中发生错误")
            self.log_api_call(None, request, 500, self.start_time, False, str(e))
            return Response(response_data, status=get_http_status(response_data['code']))

class QueryCardView(BaseApiView):
    """
    卡密查询API

    查询卡密的详细信息，包括使用记录和设备绑定信息。
    """

    @swagger_auto_schema(
        operation_description="查询卡密信息",
        request_body=CardQueryRequestSerializer,
        responses={
            200: CardQueryResponseSerializer,
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        tags=['卡密查询']
    )
    @api_monitor
    @require_api_key
    def post(self, request):
        """查询卡密信息"""
        try:
            # 验证请求数据
            serializer = CardQueryRequestSerializer(data=request.parsed_data)
            if not serializer.is_valid():
                error_msg = '; '.join([f"{k}: {', '.join(v)}" for k, v in serializer.errors.items()])
                response_data = ApiResponse.error(ApiErrorCode.CARD_ERROR, f"参数验证失败: {error_msg}")
                self.log_api_call(request.api_key_obj, request, 400, self.start_time, False, error_msg)
                return Response(response_data, status=get_http_status(response_data['code']))

            validated_data = serializer.validated_data
            card_key = validated_data['card_key']

            # 调用业务逻辑服务
            success, response_data = CardQueryService.query_card(request.api_key_obj, card_key)

            # 记录API调用日志
            status_code = get_http_status(response_data['code']) if 'code' in response_data else (200 if success else 404)
            self.log_api_call(
                request.api_key_obj, request, status_code,
                self.start_time, success, response_data.get('message', '')
            )

            return Response(response_data, status=status_code)

        except Exception as e:
            logger.error(f"卡密查询异常: {e}", exc_info=True)
            response_data = ApiResponse.system_error("查询过程中发生错误")
            self.log_api_call(None, request, 500, self.start_time, False, str(e))
            return Response(response_data, status=get_http_status(response_data['code']))


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    API健康检查端点

    返回API服务的健康状态信息。
    """
    try:
        from django.db import connection

        # 检查数据库连接
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        # 检查基本统计
        total_api_keys = ApiKey.objects.count()
        total_cards = Card.objects.count()

        health_data = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'version': '1.0.0',
            'database': 'connected',
            'stats': {
                'total_api_keys': total_api_keys,
                'total_cards': total_cards,
                'active_api_keys': ApiKey.objects.filter(is_active=True).count()
            }
        }

        return Response(health_data, status=200)

    except Exception as e:
        logger.error(f"健康检查失败: {e}", exc_info=True)
        return Response({
            'status': 'unhealthy',
            'timestamp': timezone.now().isoformat(),
            'error': str(e)
        }, status=503)


class ApiStatsView(BaseApiView):
    """
    API统计信息端点

    提供API使用统计和性能指标。
    """

    @swagger_auto_schema(
        operation_description="获取API统计信息",
        manual_parameters=[
            openapi.Parameter(
                'api_key', openapi.IN_QUERY,
                description="API密钥（可选，不提供则返回全局统计）",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'days', openapi.IN_QUERY,
                description="统计天数（默认7天）",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: "统计信息",
            401: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        tags=['API统计']
    )
    @api_monitor
    def get(self, request):
        """获取API统计信息"""
        try:
            # 获取查询参数
            api_key = request.GET.get('api_key')
            days = int(request.GET.get('days', 7))

            # 验证API密钥（如果提供）
            api_key_obj = None
            if api_key:
                api_key_obj, error_response = self.validate_api_key(api_key)
                if error_response:
                    return Response(error_response, status=get_http_status(error_response['code']))

            # 获取统计数据
            from .services import ApiStatsService
            stats_data = ApiStatsService.get_api_stats(api_key_obj, days)

            response_data = ApiResponse.success(stats_data, '统计信息获取成功')
            return Response(response_data, status=200)

        except ValueError as e:
            response_data = ApiResponse.error(ApiErrorCode.CARD_ERROR, f"参数错误: {str(e)}")
            return Response(response_data, status=get_http_status(response_data['code']))
        except Exception as e:
            logger.error(f"获取API统计失败: {e}", exc_info=True)
            response_data = ApiResponse.system_error("获取统计信息失败")
            return Response(response_data, status=get_http_status(response_data['code']))


@csrf_exempt
@require_http_methods(["POST"])
def toggle_api_key_status(request, pk):
    """切换API密钥状态"""
    try:
        # 检查用户权限
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)

        api_key = get_object_or_404(ApiKey, pk=pk)

        # 检查权限：只有创建者或超级用户可以修改
        if api_key.created_by != request.user and not request.user.is_superuser:
            return JsonResponse({'success': False, 'message': '没有权限修改此API密钥'}, status=403)

        # 切换状态
        api_key.is_active = not api_key.is_active
        api_key.save()

        # 记录操作日志
        action = "启用" if api_key.is_active else "禁用"
        logger.info(f"用户 {request.user.username} {action}了API密钥 {api_key.name}")

        return JsonResponse({
            'success': True,
            'message': f'API密钥已{action}',
            'new_status': api_key.is_active,
            'status_text': '启用' if api_key.is_active else '禁用'
        })

    except Exception as e:
        logger.error(f"切换API密钥状态失败: {e}", exc_info=True)
        return JsonResponse({'success': False, 'message': '操作失败，请重试'}, status=500)


# API管理页面视图
class ApiKeyListView(ApprovedUserRequiredMixin, ListView):
    """API密钥列表视图"""
    model = ApiKey
    template_name = 'api/key_list.html'
    context_object_name = 'api_keys'
    paginate_by = 20

    def get_queryset(self):
        queryset = ApiKey.objects.select_related('created_by').order_by('-created_at')

        # 搜索功能
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(key__icontains=search) |
                Q(created_by__username__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class ApiKeyCreateView(ApprovedUserRequiredMixin, CreateView):
    """创建API密钥视图"""
    model = ApiKey
    form_class = ApiKeyForm
    template_name = 'api/key_create.html'
    success_url = reverse_lazy('api:key_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'API密钥创建成功！')
        return super().form_valid(form)


class ApiKeyUpdateView(ApprovedUserRequiredMixin, UpdateView):
    """编辑API密钥视图"""
    model = ApiKey
    form_class = ApiKeyForm
    template_name = 'api/key_edit.html'
    success_url = reverse_lazy('api:key_list')

    def form_valid(self, form):
        messages.success(self.request, 'API密钥更新成功！')
        return super().form_valid(form)


class ApiKeyDeleteView(ApprovedUserRequiredMixin, DeleteView):
    """删除API密钥视图"""
    model = ApiKey
    template_name = 'api/key_delete.html'
    success_url = reverse_lazy('api:key_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'API密钥删除成功！')
        return super().delete(request, *args, **kwargs)


class ApiCallLogListView(ApprovedUserRequiredMixin, ListView):
    """API调用记录列表视图"""
    model = ApiCallLog
    template_name = 'api/call_logs.html'
    context_object_name = 'logs'
    paginate_by = 50

    def get_queryset(self):
        queryset = ApiCallLog.objects.select_related('api_key').order_by('-call_time')

        # 搜索功能
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(api_key__name__icontains=search) |
                Q(endpoint__icontains=search) |
                Q(ip_address__icontains=search)
            )

        # 筛选功能
        success = self.request.GET.get('success')
        if success:
            queryset = queryset.filter(success=success == 'true')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['success'] = self.request.GET.get('success', '')
        return context
