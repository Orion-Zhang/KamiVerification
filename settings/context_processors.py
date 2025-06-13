from .models import SystemSettings


def system_settings(request):
    """
    系统设置上下文处理器
    在所有模板中提供系统设置数据
    """
    try:
        settings = SystemSettings.get_settings()
        return {
            'settings': settings,
            'site_name': settings.site_name,
            'site_subtitle': settings.site_subtitle,
            'site_description': settings.site_description,
        }
    except Exception:
        # 如果获取设置失败，返回默认值
        return {
            'settings': None,
            'site_name': 'Killua',
            'site_subtitle': '在线卡密验证系统',
            'site_description': '为您的软件产品提供安全、可靠、现代化的在线卡密验证服务。',
        }
