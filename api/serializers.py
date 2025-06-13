# -*- coding: utf-8 -*-
"""
API序列化器
==========

定义API输入输出的序列化器，确保数据格式的一致性和验证。

作者：Augment Agent
日期：2024
"""

from rest_framework import serializers
from django.utils import timezone
from cards.models import Card, DeviceBinding, VerificationLog
from .models import ApiKey, ApiCallLog


class CardVerifyRequestSerializer(serializers.Serializer):
    """卡密验证请求序列化器"""
    
    api_key = serializers.CharField(
        max_length=64,
        required=True,
        help_text="API密钥"
    )
    
    card_key = serializers.CharField(
        max_length=64,
        required=True,
        help_text="卡密"
    )
    
    device_id = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        help_text="设备ID（可选）"
    )
    
    def validate_api_key(self, value):
        """验证API密钥格式"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("API密钥不能为空")
        return value.strip()
    
    def validate_card_key(self, value):
        """验证卡密格式"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("卡密不能为空")
        return value.strip()
    
    def validate_device_id(self, value):
        """验证设备ID格式"""
        if value and len(value) > 255:
            raise serializers.ValidationError("设备ID长度不能超过255个字符")
        return value.strip() if value else None


class CardQueryRequestSerializer(serializers.Serializer):
    """卡密查询请求序列化器"""
    
    api_key = serializers.CharField(
        max_length=64,
        required=True,
        help_text="API密钥"
    )
    
    card_key = serializers.CharField(
        max_length=64,
        required=True,
        help_text="卡密"
    )
    
    def validate_api_key(self, value):
        """验证API密钥格式"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("API密钥不能为空")
        return value.strip()
    
    def validate_card_key(self, value):
        """验证卡密格式"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("卡密不能为空")
        return value.strip()


class CardInfoSerializer(serializers.ModelSerializer):
    """卡密信息序列化器"""
    
    remaining_count = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = Card
        fields = [
            'card_type', 'status', 'expire_date',
            'total_count', 'used_count', 'remaining_count',
            'first_used_at', 'last_used_at', 'is_expired',
            'allow_multi_device', 'max_devices'
        ]
    
    def get_remaining_count(self, obj):
        """获取剩余次数"""
        if obj.card_type == 'count' and obj.total_count is not None:
            return max(0, obj.total_count - obj.used_count)
        return None
    
    def get_is_expired(self, obj):
        """获取是否过期"""
        return obj.is_expired


class DeviceBindingSerializer(serializers.ModelSerializer):
    """设备绑定序列化器"""
    
    class Meta:
        model = DeviceBinding
        fields = [
            'device_id', 'device_name', 'ip_address',
            'first_bind_time', 'last_active_time', 'is_active'
        ]


class VerificationLogSerializer(serializers.ModelSerializer):
    """验证记录序列化器"""
    
    class Meta:
        model = VerificationLog
        fields = [
            'verification_time', 'ip_address', 'success', 'error_message'
        ]


class CardVerifyResponseSerializer(serializers.Serializer):
    """卡密验证响应序列化器"""
    
    code = serializers.IntegerField(help_text="错误码")
    success = serializers.BooleanField(help_text="是否成功")
    message = serializers.CharField(help_text="响应消息")
    data = serializers.DictField(required=False, help_text="响应数据")
    
    def to_representation(self, instance):
        """自定义序列化输出"""
        if isinstance(instance, dict):
            return instance
        return super().to_representation(instance)


class CardQueryResponseSerializer(serializers.Serializer):
    """卡密查询响应序列化器"""
    
    success = serializers.BooleanField(help_text="是否成功")
    message = serializers.CharField(required=False, help_text="响应消息")
    data = serializers.DictField(required=False, help_text="卡密详细信息")


class ApiKeySerializer(serializers.ModelSerializer):
    """API密钥序列化器"""
    
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = ApiKey
        fields = [
            'id', 'name', 'key', 'is_active', 'rate_limit',
            'created_at', 'last_used_at', 'usage_count',
            'created_by_username'
        ]
        read_only_fields = ['key', 'created_at', 'last_used_at', 'usage_count']


class ApiCallLogSerializer(serializers.ModelSerializer):
    """API调用记录序列化器"""
    
    api_key_name = serializers.CharField(source='api_key.name', read_only=True)
    
    class Meta:
        model = ApiCallLog
        fields = [
            'id', 'api_key_name', 'endpoint', 'method',
            'ip_address', 'response_code', 'response_time',
            'call_time', 'success', 'error_message'
        ]


class ApiStatsSerializer(serializers.Serializer):
    """API统计信息序列化器"""
    
    total_calls = serializers.IntegerField(help_text="总调用次数")
    successful_calls = serializers.IntegerField(help_text="成功调用次数")
    failed_calls = serializers.IntegerField(help_text="失败调用次数")
    success_rate = serializers.FloatField(help_text="成功率")
    avg_response_time = serializers.FloatField(help_text="平均响应时间(ms)")
    calls_today = serializers.IntegerField(help_text="今日调用次数")
    calls_this_hour = serializers.IntegerField(help_text="本小时调用次数")
    
    # 按时间段统计
    hourly_stats = serializers.ListField(
        child=serializers.DictField(),
        help_text="按小时统计",
        required=False
    )
    
    daily_stats = serializers.ListField(
        child=serializers.DictField(),
        help_text="按天统计",
        required=False
    )
    
    # 按API密钥统计
    top_api_keys = serializers.ListField(
        child=serializers.DictField(),
        help_text="使用最多的API密钥",
        required=False
    )
    
    # 按端点统计
    endpoint_stats = serializers.ListField(
        child=serializers.DictField(),
        help_text="按端点统计",
        required=False
    )


class ErrorResponseSerializer(serializers.Serializer):
    """错误响应序列化器"""
    
    code = serializers.IntegerField(help_text="错误码")
    success = serializers.BooleanField(default=False, help_text="是否成功")
    message = serializers.CharField(help_text="错误消息")
    data = serializers.DictField(required=False, help_text="额外数据")
    
    # 调试信息（仅在DEBUG模式下返回）
    debug_info = serializers.DictField(required=False, help_text="调试信息")


class PaginatedResponseSerializer(serializers.Serializer):
    """分页响应序列化器"""
    
    count = serializers.IntegerField(help_text="总记录数")
    next = serializers.URLField(required=False, allow_null=True, help_text="下一页URL")
    previous = serializers.URLField(required=False, allow_null=True, help_text="上一页URL")
    results = serializers.ListField(help_text="结果列表")


# 输入验证辅助函数
def validate_device_id_format(device_id):
    """验证设备ID格式"""
    if not device_id:
        return True
    
    # 设备ID应该是字母数字组合，可以包含连字符和下划线
    import re
    pattern = r'^[a-zA-Z0-9_-]+$'
    return re.match(pattern, device_id) is not None


def validate_api_key_format(api_key):
    """验证API密钥格式"""
    if not api_key:
        return False
    
    # API密钥应该是32位十六进制字符串
    import re
    pattern = r'^[a-fA-F0-9]{32}$'
    return re.match(pattern, api_key) is not None


def sanitize_input(value, max_length=None):
    """清理输入数据"""
    if not isinstance(value, str):
        return value
    
    # 移除前后空白
    value = value.strip()
    
    # 限制长度
    if max_length and len(value) > max_length:
        value = value[:max_length]
    
    # 移除潜在的危险字符
    dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
    for char in dangerous_chars:
        value = value.replace(char, '')
    
    return value
