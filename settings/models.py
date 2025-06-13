from django.db import models
from django.core.validators import FileExtensionValidator
import os


class SystemSettings(models.Model):
    """系统设置模型"""

    # 网站基本信息
    site_name = models.CharField(max_length=100, default='Killua', verbose_name='网站名称')
    site_subtitle = models.CharField(max_length=200, default='在线卡密验证系统', verbose_name='网站副标题')
    site_description = models.TextField(
        default='为您的软件产品提供安全、可靠、现代化的在线卡密验证服务。',
        verbose_name='网站描述'
    )

    # 英雄区域图片
    hero_image = models.ImageField(
        upload_to='settings/hero/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'svg', 'webp'])],
        verbose_name='英雄区域图片',
        help_text='推荐尺寸: 600x400px，支持 JPG、PNG、SVG、WebP 格式'
    )

    # Logo 图片
    logo_image = models.ImageField(
        upload_to='settings/logo/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'svg', 'webp'])],
        verbose_name='Logo图片',
        help_text='推荐尺寸: 200x200px，支持 JPG、PNG、SVG、WebP 格式'
    )

    # 网站图标
    favicon = models.ImageField(
        upload_to='settings/favicon/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['ico', 'png'])],
        verbose_name='网站图标',
        help_text='推荐尺寸: 32x32px 或 64x64px，支持 ICO、PNG 格式'
    )

    # 主题颜色设置
    primary_color = models.CharField(
        max_length=7,
        default='#3b82f6',
        verbose_name='主色调',
        help_text='十六进制颜色代码，如 #3b82f6'
    )

    accent_color = models.CharField(
        max_length=7,
        default='#06b6d4',
        verbose_name='强调色',
        help_text='十六进制颜色代码，如 #06b6d4'
    )

    # 功能开关
    enable_registration = models.BooleanField(default=True, verbose_name='允许用户注册')
    enable_api_docs = models.BooleanField(default=True, verbose_name='显示API文档')
    enable_statistics = models.BooleanField(default=True, verbose_name='显示统计信息')

    # 联系信息
    contact_email = models.EmailField(blank=True, verbose_name='联系邮箱')
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name='联系电话')

    # 社交媒体链接
    github_url = models.URLField(blank=True, verbose_name='GitHub链接')
    website_url = models.URLField(blank=True, verbose_name='官方网站')

    # 系统维护
    maintenance_mode = models.BooleanField(default=False, verbose_name='维护模式')
    maintenance_message = models.TextField(
        blank=True,
        default='系统正在维护中，请稍后再试。',
        verbose_name='维护提示信息'
    )

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '系统设置'
        verbose_name_plural = '系统设置'

    def __str__(self):
        return f'{self.site_name} - 系统设置'

    @classmethod
    def get_settings(cls):
        """获取系统设置，如果不存在则创建默认设置"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings

    def delete(self, *args, **kwargs):
        """删除时同时删除关联的图片文件"""
        if self.hero_image:
            if os.path.isfile(self.hero_image.path):
                os.remove(self.hero_image.path)

        if self.logo_image:
            if os.path.isfile(self.logo_image.path):
                os.remove(self.logo_image.path)

        if self.favicon:
            if os.path.isfile(self.favicon.path):
                os.remove(self.favicon.path)

        super().delete(*args, **kwargs)
