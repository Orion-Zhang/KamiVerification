from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


class ApprovedUserRequiredMixin(LoginRequiredMixin):
    """要求用户已登录且已审批通过的混入类"""
    
    def dispatch(self, request, *args, **kwargs):
        # 首先检查是否登录
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # 超级管理员直接通过
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        
        # 检查普通管理员的审批状态
        if request.user.status != 'approved':
            messages.error(request, '您的账户尚未通过审批，无法访问此页面。')
            return redirect('accounts:pending')
        
        return super().dispatch(request, *args, **kwargs)


class SuperUserRequiredMixin(UserPassesTestMixin):
    """要求超级管理员权限的混入类"""
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, '您没有权限访问此页面。')
        return super().handle_no_permission()


def approved_user_required(view_func):
    """要求用户已审批通过的装饰器"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        # 超级管理员直接通过
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # 检查普通管理员的审批状态
        if request.user.status != 'approved':
            messages.error(request, '您的账户尚未通过审批，无法访问此页面。')
            return redirect('accounts:pending')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def superuser_required(view_func):
    """要求超级管理员权限的装饰器"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        if not request.user.is_superuser:
            messages.error(request, '您没有权限访问此页面。')
            raise PermissionDenied
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def is_superuser(user):
    """检查用户是否为超级管理员"""
    return user.is_superuser


def is_approved_user(user):
    """检查用户是否为已审批的用户"""
    return user.is_superuser or user.status == 'approved'
