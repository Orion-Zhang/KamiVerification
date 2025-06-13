from django.contrib import admin
from django.utils.html import format_html
from .models import Card, DeviceBinding, VerificationLog


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('card_key_display', 'card_type', 'status', 'created_by', 'created_at', 'expire_info')
    list_filter = ('card_type', 'status', 'created_at')
    search_fields = ('card_key', 'card_key_hash', 'created_by__username')
    readonly_fields = ('card_key_hash', 'created_at', 'first_used_at', 'last_used_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('基本信息', {
            'fields': ('card_key', 'card_key_hash', 'card_type', 'status')
        }),
        ('时间卡设置', {
            'fields': ('valid_days', 'expire_date'),
            'classes': ('collapse',)
        }),
        ('次数卡设置', {
            'fields': ('total_count', 'used_count'),
            'classes': ('collapse',)
        }),
        ('设备绑定', {
            'fields': ('allow_multi_device', 'max_devices')
        }),
        ('使用信息', {
            'fields': ('first_used_at', 'last_used_at', 'created_by', 'created_at')
        }),
        ('备注', {
            'fields': ('note',)
        }),
    )

    def card_key_display(self, obj):
        """显示部分卡密"""
        return f"{obj.card_key[:8]}***"
    card_key_display.short_description = '卡密'

    def expire_info(self, obj):
        """显示过期信息"""
        if obj.card_type == 'time' and obj.expire_date:
            if obj.is_expired:
                return format_html('<span style="color: red;">已过期</span>')
            return obj.expire_date.strftime('%Y-%m-%d %H:%M')
        elif obj.card_type == 'count':
            remaining = obj.remaining_count
            if remaining <= 0:
                return format_html('<span style="color: red;">已用完</span>')
            return f"剩余 {remaining} 次"
        return '-'
    expire_info.short_description = '过期信息'


@admin.register(DeviceBinding)
class DeviceBindingAdmin(admin.ModelAdmin):
    list_display = ('card', 'device_id_display', 'device_name', 'ip_address', 'first_bind_time', 'is_active')
    list_filter = ('is_active', 'first_bind_time')
    search_fields = ('card__card_key', 'device_id', 'device_name', 'ip_address')
    readonly_fields = ('first_bind_time', 'last_active_time')
    ordering = ('-last_active_time',)

    def device_id_display(self, obj):
        """显示部分设备ID"""
        return f"{obj.device_id[:16]}..."
    device_id_display.short_description = '设备ID'


@admin.register(VerificationLog)
class VerificationLogAdmin(admin.ModelAdmin):
    list_display = ('card', 'ip_address', 'verification_time', 'success', 'api_key_display')
    list_filter = ('success', 'verification_time')
    search_fields = ('card__card_key', 'ip_address', 'api_key')
    readonly_fields = ('card', 'device_binding', 'ip_address', 'user_agent',
                      'verification_time', 'success', 'error_message', 'api_key')
    ordering = ('-verification_time',)

    def api_key_display(self, obj):
        """显示部分API密钥"""
        if obj.api_key:
            return f"{obj.api_key[:8]}..."
        return '-'
    api_key_display.short_description = 'API密钥'
