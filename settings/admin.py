from django.contrib import admin
from django.utils.html import format_html
from .models import SystemSettings


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    """系统设置管理界面"""

    list_display = ['site_name', 'site_subtitle', 'primary_color_preview', 'updated_at']

    fieldsets = (
        ('网站基本信息', {
            'fields': ('site_name', 'site_subtitle', 'site_description')
        }),
        ('图片设置', {
            'fields': ('hero_image', 'logo_image', 'favicon'),
            'description': '上传自定义图片来个性化您的网站外观'
        }),
        ('主题颜色', {
            'fields': ('primary_color', 'accent_color'),
            'description': '自定义网站的主题颜色'
        }),
        ('功能开关', {
            'fields': ('enable_registration', 'enable_api_docs', 'enable_statistics'),
            'classes': ('collapse',)
        }),
        ('联系信息', {
            'fields': ('contact_email', 'contact_phone'),
            'classes': ('collapse',)
        }),
        ('社交媒体', {
            'fields': ('github_url', 'website_url'),
            'classes': ('collapse',)
        }),
        ('系统维护', {
            'fields': ('maintenance_mode', 'maintenance_message'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def primary_color_preview(self, obj):
        """显示主色调预览"""
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 3px; display: inline-block;"></div> {}',
            obj.primary_color,
            obj.primary_color
        )
    primary_color_preview.short_description = '主色调预览'

    def has_add_permission(self, request):
        """只允许存在一个系统设置实例"""
        return not SystemSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """不允许删除系统设置"""
        return False
