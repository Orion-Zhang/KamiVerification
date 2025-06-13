from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class ApiKey(models.Model):
    """API密钥模型"""
    name = models.CharField('密钥名称', max_length=100)
    key = models.CharField('密钥', max_length=64, unique=True)
    is_active = models.BooleanField('是否启用', default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建者')
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    last_used_at = models.DateTimeField('最后使用时间', null=True, blank=True)
    usage_count = models.IntegerField('使用次数', default=0)
    rate_limit = models.IntegerField('频率限制(次/分钟)', default=60)

    class Meta:
        verbose_name = 'API密钥'
        verbose_name_plural = 'API密钥'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = str(uuid.uuid4()).replace('-', '')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.key[:8]}...)"


class ApiCallLog(models.Model):
    """API调用记录"""
    api_key = models.ForeignKey(ApiKey, on_delete=models.CASCADE, verbose_name='API密钥')
    endpoint = models.CharField('接口端点', max_length=255)
    method = models.CharField('请求方法', max_length=10)
    ip_address = models.GenericIPAddressField('IP地址')
    user_agent = models.TextField('用户代理', blank=True)
    request_data = models.JSONField('请求数据', null=True, blank=True)
    response_code = models.IntegerField('响应状态码')
    response_time = models.FloatField('响应时间(ms)')
    call_time = models.DateTimeField('调用时间', default=timezone.now)
    success = models.BooleanField('调用成功', default=True)
    error_message = models.TextField('错误信息', blank=True)

    class Meta:
        verbose_name = 'API调用记录'
        verbose_name_plural = 'API调用记录'
        ordering = ['-call_time']

    def __str__(self):
        return f"{self.api_key.name} - {self.endpoint} - {self.call_time}"
