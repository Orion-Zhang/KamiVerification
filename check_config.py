#!/usr/bin/env python
"""
CardVerification 配置检查脚本
检查生产环境配置是否正确
"""

import os
import sys
import django
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CardVerification.settings')
django.setup()

from django.conf import settings
from django.core.management import execute_from_command_line
from django.db import connection
from django.core.cache import cache


class ConfigChecker:
    """配置检查器"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success = []
    
    def log_error(self, message):
        self.errors.append(f"❌ {message}")
    
    def log_warning(self, message):
        self.warnings.append(f"⚠️  {message}")
    
    def log_success(self, message):
        self.success.append(f"✅ {message}")
    
    def check_basic_settings(self):
        """检查基础设置"""
        print("🔍 检查基础设置...")
        
        # 检查DEBUG设置
        if settings.DEBUG:
            self.log_warning("DEBUG模式已启用，生产环境应设置为False")
        else:
            self.log_success("DEBUG模式已正确关闭")
        
        # 检查SECRET_KEY
        if settings.SECRET_KEY == 'django-insecure-^iq$@6z+n=nhmdx0)9vx8w9o85ls=+%bz9p&qd79$3=+_#!jbo':
            self.log_error("SECRET_KEY使用默认值，生产环境必须更改")
        else:
            self.log_success("SECRET_KEY已正确设置")
        
        # 检查ALLOWED_HOSTS
        if not settings.ALLOWED_HOSTS or settings.ALLOWED_HOSTS == ['127.0.0.1', 'localhost', 'testserver']:
            self.log_warning("ALLOWED_HOSTS可能需要配置生产域名")
        else:
            self.log_success(f"ALLOWED_HOSTS已配置: {settings.ALLOWED_HOSTS}")
    
    def check_database_config(self):
        """检查数据库配置"""
        print("🔍 检查数据库配置...")
        
        db_config = settings.DATABASES['default']
        
        if db_config['ENGINE'] == 'django.db.backends.sqlite3':
            self.log_warning("使用SQLite数据库，生产环境建议使用PostgreSQL")
        else:
            self.log_success(f"使用生产数据库: {db_config['ENGINE']}")
        
        # 测试数据库连接
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.log_success("数据库连接正常")
        except Exception as e:
            self.log_error(f"数据库连接失败: {e}")
    
    def check_cache_config(self):
        """检查缓存配置"""
        print("🔍 检查缓存配置...")
        
        if hasattr(settings, 'CACHES'):
            cache_backend = settings.CACHES['default']['BACKEND']
            if 'redis' in cache_backend.lower():
                self.log_success("已配置Redis缓存")
                
                # 测试缓存连接
                try:
                    cache.set('test_key', 'test_value', 10)
                    if cache.get('test_key') == 'test_value':
                        self.log_success("缓存连接正常")
                        cache.delete('test_key')
                    else:
                        self.log_error("缓存读写测试失败")
                except Exception as e:
                    self.log_error(f"缓存连接失败: {e}")
            else:
                self.log_warning("未配置Redis缓存，建议生产环境使用Redis")
        else:
            self.log_warning("未配置缓存系统")
    
    def check_security_settings(self):
        """检查安全设置"""
        print("🔍 检查安全设置...")
        
        security_settings = [
            ('SECURE_SSL_REDIRECT', '强制HTTPS重定向'),
            ('SECURE_HSTS_SECONDS', 'HSTS安全头'),
            ('SESSION_COOKIE_SECURE', 'Cookie安全设置'),
            ('CSRF_COOKIE_SECURE', 'CSRF Cookie安全'),
        ]
        
        for setting_name, description in security_settings:
            if hasattr(settings, setting_name):
                value = getattr(settings, setting_name)
                if value:
                    self.log_success(f"{description}已启用")
                else:
                    self.log_warning(f"{description}未启用")
            else:
                self.log_warning(f"{description}未配置")
    
    def check_logging_config(self):
        """检查日志配置"""
        print("🔍 检查日志配置...")
        
        if hasattr(settings, 'LOGGING'):
            self.log_success("日志系统已配置")
            
            # 检查日志目录
            logs_dir = Path('logs')
            if logs_dir.exists():
                self.log_success("日志目录存在")
            else:
                self.log_warning("日志目录不存在，将自动创建")
                logs_dir.mkdir(exist_ok=True)
        else:
            self.log_warning("未配置日志系统")
    
    def check_static_files(self):
        """检查静态文件配置"""
        print("🔍 检查静态文件配置...")
        
        static_root = Path(settings.STATIC_ROOT)
        if static_root.exists():
            self.log_success("静态文件目录存在")
        else:
            self.log_warning("静态文件目录不存在，请运行 collectstatic")
        
        # 检查静态文件存储
        if not settings.DEBUG:
            if hasattr(settings, 'STATICFILES_STORAGE'):
                if 'Manifest' in settings.STATICFILES_STORAGE:
                    self.log_success("已配置静态文件版本控制")
                else:
                    self.log_warning("建议配置静态文件版本控制")
    
    def check_email_config(self):
        """检查邮件配置"""
        print("🔍 检查邮件配置...")
        
        if hasattr(settings, 'EMAIL_HOST') and settings.EMAIL_HOST:
            self.log_success(f"邮件服务器已配置: {settings.EMAIL_HOST}")
        else:
            self.log_warning("未配置邮件服务器")
    
    def run_all_checks(self):
        """运行所有检查"""
        print("🚀 开始配置检查...\n")
        
        self.check_basic_settings()
        print()
        
        self.check_database_config()
        print()
        
        self.check_cache_config()
        print()
        
        self.check_security_settings()
        print()
        
        self.check_logging_config()
        print()
        
        self.check_static_files()
        print()
        
        self.check_email_config()
        print()
        
        self.print_summary()
    
    def print_summary(self):
        """打印检查结果摘要"""
        print("=" * 60)
        print("📊 配置检查结果摘要")
        print("=" * 60)
        
        if self.success:
            print("\n✅ 成功项目:")
            for item in self.success:
                print(f"  {item}")
        
        if self.warnings:
            print("\n⚠️  警告项目:")
            for item in self.warnings:
                print(f"  {item}")
        
        if self.errors:
            print("\n❌ 错误项目:")
            for item in self.errors:
                print(f"  {item}")
        
        print("\n" + "=" * 60)
        
        if self.errors:
            print("❌ 配置检查发现错误，请修复后再部署到生产环境")
            return False
        elif self.warnings:
            print("⚠️  配置检查发现警告，建议优化后部署到生产环境")
            return True
        else:
            print("✅ 配置检查通过，可以部署到生产环境")
            return True


def main():
    """主函数"""
    checker = ConfigChecker()
    success = checker.run_all_checks()
    
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
