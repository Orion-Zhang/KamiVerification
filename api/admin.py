from django.contrib import admin
from .models import ApiKey, ApiCallLog


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'key_display', 'is_active', 'created_by', 'usage_count', 'last_used_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'key', 'created_by__username')
    readonly_fields = ('key', 'created_at', 'last_used_at', 'usage_count')
    ordering = ('-created_at',)

    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'key', 'is_active')
        }),
        ('限制设置', {
            'fields': ('rate_limit',)
        }),
        ('使用统计', {
            'fields': ('usage_count', 'last_used_at', 'created_by', 'created_at')
        }),
    )

    def key_display(self, obj):
        """显示部分密钥"""
        return f"{obj.key[:8]}..."
    key_display.short_description = 'API密钥'


@admin.register(ApiCallLog)
class ApiCallLogAdmin(admin.ModelAdmin):
    list_display = ('api_key', 'endpoint', 'method', 'response_code', 'call_time', 'success')
    list_filter = ('method', 'success', 'response_code', 'call_time')
    search_fields = ('api_key__name', 'endpoint', 'ip_address')
    readonly_fields = ('api_key', 'endpoint', 'method', 'ip_address', 'user_agent',
                      'request_data', 'response_code', 'response_time', 'call_time',
                      'success', 'error_message')
    ordering = ('-call_time',)
