from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils import timezone


class CustomUserManager(UserManager):
    """自定义用户管理器"""

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """创建超级管理员"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'super_admin')
        extra_fields.setdefault('status', 'approved')
        extra_fields.setdefault('approved_at', timezone.now())

        if extra_fields.get('is_staff') is not True:
            raise ValueError('超级管理员必须设置 is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('超级管理员必须设置 is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)


class CustomUser(AbstractUser):
    """扩展用户模型"""
    ROLE_CHOICES = [
        ('super_admin', '超级管理员'),
        ('admin', '普通管理员'),
    ]

    STATUS_CHOICES = [
        ('pending', '待审批'),
        ('approved', '已审批'),
        ('rejected', '已拒绝'),
    ]

    email = models.EmailField('邮箱', unique=True)
    phone = models.CharField('手机号', max_length=11, blank=True)
    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES, default='admin')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    approved_at = models.DateTimeField('审批时间', null=True, blank=True)
    approved_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='审批人'
    )

    # 使用自定义用户管理器
    objects = CustomUserManager()

    class Meta:
        verbose_name = '管理员'
        verbose_name_plural = '管理员'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def is_approved(self):
        """检查用户是否已审批"""
        return self.is_superuser or self.status == 'approved'

    def can_access_admin(self):
        """检查用户是否可以访问Django admin"""
        return self.is_superuser

    def can_access_dashboard(self):
        """检查用户是否可以访问前端控制面板"""
        return self.is_superuser or self.status == 'approved'

    def save(self, *args, **kwargs):
        """重写保存方法，确保超级管理员自动审批"""
        # 如果是超级管理员，自动设置为已审批状态
        if self.is_superuser:
            self.role = 'super_admin'
            self.status = 'approved'
            if not self.approved_at:
                self.approved_at = timezone.now()

        # 如果是新创建的普通管理员，保持默认的待审批状态
        elif not self.pk and not self.is_superuser:
            self.role = 'admin'
            self.status = 'pending'

        super().save(*args, **kwargs)


class LoginLog(models.Model):
    """登录日志"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='用户')
    ip_address = models.GenericIPAddressField('IP地址')
    user_agent = models.TextField('用户代理', blank=True)
    login_time = models.DateTimeField('登录时间', default=timezone.now)
    success = models.BooleanField('登录成功', default=True)

    class Meta:
        verbose_name = '登录日志'
        verbose_name_plural = '登录日志'
        ordering = ['-login_time']

    def __str__(self):
        return f"{self.user.username} - {self.login_time}"
