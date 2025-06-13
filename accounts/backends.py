from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib import messages

User = get_user_model()


class CustomAuthenticationBackend(ModelBackend):
    """自定义认证后端，实现审批状态检查"""
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """认证用户并检查审批状态"""
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        
        # 验证密码
        if user.check_password(password):
            # 检查用户是否为超级管理员
            if user.is_superuser:
                return user
            
            # 检查普通管理员的审批状态
            if user.status != 'approved':
                if request:
                    if user.status == 'pending':
                        messages.error(request, '您的账户正在等待管理员审批，请耐心等待。')
                    elif user.status == 'rejected':
                        messages.error(request, '您的账户申请已被拒绝，请联系管理员。')
                return None
            
            return user
        
        return None
    
    def user_can_authenticate(self, user):
        """检查用户是否可以认证"""
        # 超级管理员总是可以认证
        if user.is_superuser:
            return True
        
        # 普通管理员需要审批通过才能认证
        return user.status == 'approved' and user.is_active


class AdminAuthenticationBackend(ModelBackend):
    """Django Admin专用认证后端，只允许超级管理员登录"""
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """只允许超级管理员认证"""
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        
        # 验证密码
        if user.check_password(password):
            # 只允许超级管理员登录admin
            if user.is_superuser:
                return user
            else:
                if request:
                    messages.error(request, '您没有权限访问管理后台。')
                return None
        
        return None
    
    def user_can_authenticate(self, user):
        """只有超级管理员可以认证"""
        return user.is_superuser and user.is_active
