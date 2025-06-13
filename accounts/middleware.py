from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse


class AdminAccessMiddleware:
    """确保只有超级管理员可以访问Django admin的中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 检查是否是admin路径
        if request.path.startswith('/admin/'):
            # 如果用户已登录但不是超级管理员
            if request.user.is_authenticated and not request.user.is_superuser:
                messages.error(request, '您没有权限访问管理后台，只有超级管理员可以访问。')
                return HttpResponseRedirect('/')
            
            # 如果用户未登录，让Django的默认认证处理
        
        response = self.get_response(request)
        return response
