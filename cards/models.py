from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import hashlib
import uuid

User = get_user_model()


class Card(models.Model):
    """卡密模型"""
    CARD_TYPE_CHOICES = [
        ('time', '时间卡'),
        ('count', '次数卡'),
    ]

    STATUS_CHOICES = [
        ('active', '启用'),
        ('inactive', '禁用'),
        ('expired', '已过期'),
        ('used_up', '已用完'),
    ]

    card_key = models.CharField('卡密', max_length=64, unique=True)
    card_key_hash = models.CharField('卡密哈希', max_length=40, unique=True)
    card_type = models.CharField('卡密类型', max_length=10, choices=CARD_TYPE_CHOICES)
    status = models.CharField('状态', max_length=10, choices=STATUS_CHOICES, default='active')

    # 时间卡相关字段
    valid_days = models.IntegerField('有效天数', null=True, blank=True)
    expire_date = models.DateTimeField('过期时间', null=True, blank=True)

    # 次数卡相关字段
    total_count = models.IntegerField('总次数', null=True, blank=True)
    used_count = models.IntegerField('已使用次数', default=0)

    # 设备绑定相关
    allow_multi_device = models.BooleanField('允许多设备', default=False)
    max_devices = models.IntegerField('最大设备数', default=1)

    # 创建信息
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建者')
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    first_used_at = models.DateTimeField('首次使用时间', null=True, blank=True)
    last_used_at = models.DateTimeField('最后使用时间', null=True, blank=True)

    # 备注
    note = models.TextField('备注', blank=True)

    class Meta:
        verbose_name = '卡密'
        verbose_name_plural = '卡密'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.card_key_hash:
            self.card_key_hash = hashlib.sha1(self.card_key.encode()).hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.card_key[:8]}*** ({self.get_card_type_display()})"

    @property
    def is_expired(self):
        """检查是否过期"""
        if self.card_type == 'time' and self.expire_date:
            return timezone.now() > self.expire_date
        elif self.card_type == 'count':
            return self.used_count >= self.total_count
        return False

    @property
    def remaining_count(self):
        """剩余次数"""
        if self.card_type == 'count':
            return max(0, self.total_count - self.used_count)
        return None


class DeviceBinding(models.Model):
    """设备绑定模型"""
    card = models.ForeignKey(Card, on_delete=models.CASCADE, verbose_name='卡密')
    device_id = models.CharField('设备ID', max_length=255)
    device_name = models.CharField('设备名称', max_length=255, blank=True)
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    first_bind_time = models.DateTimeField('首次绑定时间', default=timezone.now)
    last_active_time = models.DateTimeField('最后活跃时间', default=timezone.now)
    is_active = models.BooleanField('是否活跃', default=True)

    class Meta:
        verbose_name = '设备绑定'
        verbose_name_plural = '设备绑定'
        unique_together = ['card', 'device_id']
        ordering = ['-last_active_time']

    def __str__(self):
        return f"{self.card} - {self.device_id[:16]}..."


class VerificationLog(models.Model):
    """验证记录模型"""
    card = models.ForeignKey(Card, on_delete=models.CASCADE, verbose_name='卡密')
    device_binding = models.ForeignKey(
        DeviceBinding,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='设备绑定'
    )
    ip_address = models.GenericIPAddressField('IP地址')
    user_agent = models.TextField('用户代理', blank=True)
    verification_time = models.DateTimeField('验证时间', default=timezone.now)
    success = models.BooleanField('验证成功', default=True)
    error_message = models.TextField('错误信息', blank=True)
    api_key = models.CharField('API密钥', max_length=64, blank=True)

    class Meta:
        verbose_name = '验证记录'
        verbose_name_plural = '验证记录'
        ordering = ['-verification_time']

    def __str__(self):
        return f"{self.card} - {self.verification_time}"
