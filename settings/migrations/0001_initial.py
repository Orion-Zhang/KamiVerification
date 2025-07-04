# Generated by Django 5.2.3 on 2025-06-12 20:58

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SystemSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_name', models.CharField(default='Killua', max_length=100, verbose_name='网站名称')),
                ('site_subtitle', models.CharField(default='在线卡密验证系统', max_length=200, verbose_name='网站副标题')),
                ('site_description', models.TextField(default='为您的软件产品提供安全、可靠、现代化的在线卡密验证服务。', verbose_name='网站描述')),
                ('hero_image', models.ImageField(blank=True, help_text='推荐尺寸: 600x400px，支持 JPG、PNG、SVG、WebP 格式', null=True, upload_to='settings/hero/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'svg', 'webp'])], verbose_name='英雄区域图片')),
                ('logo_image', models.ImageField(blank=True, help_text='推荐尺寸: 200x200px，支持 JPG、PNG、SVG、WebP 格式', null=True, upload_to='settings/logo/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'svg', 'webp'])], verbose_name='Logo图片')),
                ('favicon', models.ImageField(blank=True, help_text='推荐尺寸: 32x32px 或 64x64px，支持 ICO、PNG 格式', null=True, upload_to='settings/favicon/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['ico', 'png'])], verbose_name='网站图标')),
                ('primary_color', models.CharField(default='#3b82f6', help_text='十六进制颜色代码，如 #3b82f6', max_length=7, verbose_name='主色调')),
                ('accent_color', models.CharField(default='#06b6d4', help_text='十六进制颜色代码，如 #06b6d4', max_length=7, verbose_name='强调色')),
                ('enable_registration', models.BooleanField(default=True, verbose_name='允许用户注册')),
                ('enable_api_docs', models.BooleanField(default=True, verbose_name='显示API文档')),
                ('enable_statistics', models.BooleanField(default=True, verbose_name='显示统计信息')),
                ('contact_email', models.EmailField(blank=True, max_length=254, verbose_name='联系邮箱')),
                ('contact_phone', models.CharField(blank=True, max_length=20, verbose_name='联系电话')),
                ('github_url', models.URLField(blank=True, verbose_name='GitHub链接')),
                ('website_url', models.URLField(blank=True, verbose_name='官方网站')),
                ('maintenance_mode', models.BooleanField(default=False, verbose_name='维护模式')),
                ('maintenance_message', models.TextField(blank=True, default='系统正在维护中，请稍后再试。', verbose_name='维护提示信息')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '系统设置',
                'verbose_name_plural': '系统设置',
            },
        ),
    ]
