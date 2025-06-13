from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = '用户管理'

    def ready(self):
        """应用准备就绪时的配置"""
        from django.contrib import admin

        # 配置admin站点标题
        admin.site.site_header = 'Killua 卡密系统管理后台'
        admin.site.index_title = 'Killua 卡密系统管理后台'
