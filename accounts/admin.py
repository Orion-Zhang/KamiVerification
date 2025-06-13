from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from django.contrib.admin import AdminSite
from .models import CustomUser, LoginLog


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'role', 'status', 'created_at', 'is_active')
    list_filter = ('role', 'status', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'phone')
    ordering = ('-created_at',)

    fieldsets = UserAdmin.fieldsets + (
        ('扩展信息', {
            'fields': ('phone', 'role', 'status', 'approved_by', 'approved_at')
        }),
    )

    actions = ['approve_users', 'reject_users', 'freeze_users', 'unfreeze_users']

    def approve_users(self, request, queryset):
        """批量审批用户"""
        count = queryset.filter(status='pending').update(
            status='approved',
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'成功审批 {count} 个用户')
    approve_users.short_description = '审批选中的用户'

    def reject_users(self, request, queryset):
        """批量拒绝用户"""
        count = queryset.filter(status='pending').update(
            status='rejected',
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'成功拒绝 {count} 个用户')
    reject_users.short_description = '拒绝选中的用户'

    def freeze_users(self, request, queryset):
        """冻结用户"""
        count = queryset.filter(is_active=True, is_superuser=False).update(is_active=False)
        self.message_user(request, f'成功冻结 {count} 个用户')
    freeze_users.short_description = '冻结选中的用户'

    def unfreeze_users(self, request, queryset):
        """解冻用户"""
        count = queryset.filter(is_active=False, is_superuser=False).update(is_active=True)
        self.message_user(request, f'成功解冻 {count} 个用户')
    unfreeze_users.short_description = '解冻选中的用户'

    def has_delete_permission(self, request, obj=None):
        """只有超级管理员可以删除用户，且不能删除超级管理员"""
        if not request.user.is_superuser:
            return False
        if obj and obj.is_superuser:
            return False
        return True

    def has_change_permission(self, request, obj=None):
        """只有超级管理员可以修改用户"""
        return request.user.is_superuser


@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'login_time', 'success')
    list_filter = ('success', 'login_time')
    search_fields = ('user__username', 'ip_address')
    readonly_fields = ('user', 'ip_address', 'user_agent', 'login_time', 'success')
    ordering = ('-login_time',)
