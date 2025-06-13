import hashlib
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from django.db.models import Q, Count, Avg, Sum
from django.core.cache import cache
from cards.models import Card, DeviceBinding, VerificationLog
from .models import ApiKey, ApiCallLog
from .error_codes import ApiResponse, ApiErrorCode

logger = logging.getLogger(__name__)


class CardVerificationService:
    """卡密验证服务"""
    
    @staticmethod
    def verify_card(api_key_obj, card_key, device_id=None, request=None):
        """
        验证卡密
        
        Args:
            api_key_obj: API密钥对象
            card_key: 卡密
            device_id: 设备ID（可选）
            request: 请求对象
            
        Returns:
            tuple: (success, response_data, card_obj)
        """
        try:
            with transaction.atomic():
                # 查找卡密
                card_key_hash = hashlib.sha1(card_key.encode()).hexdigest()
                try:
                    card = Card.objects.select_for_update().get(card_key_hash=card_key_hash)
                except Card.DoesNotExist:
                    return False, ApiResponse.card_not_found(), None
                
                # 检查卡密状态
                if card.status == 'inactive':
                    return False, ApiResponse.card_disabled(), card
                elif card.status == 'expired':
                    return False, ApiResponse.card_expired(), card
                elif card.status == 'used_up':
                    return False, ApiResponse.card_used_up(), card
                
                # 检查是否过期
                if card.is_expired:
                    card.status = 'expired'
                    card.save()
                    return False, ApiResponse.card_expired(), card
                
                # 处理设备绑定
                device_binding = None
                if device_id:
                    device_binding_result = CardVerificationService._handle_device_binding(
                        card, device_id, request
                    )
                    if not device_binding_result['success']:
                        return False, device_binding_result['response'], card
                    device_binding = device_binding_result['device_binding']
                
                # 更新卡密使用信息
                if not card.first_used_at:
                    card.first_used_at = timezone.now()
                card.last_used_at = timezone.now()
                
                # 次数卡处理
                if card.card_type == 'count':
                    if card.used_count >= card.total_count:
                        card.status = 'used_up'
                        card.save()
                        return False, ApiResponse.card_used_up(), card
                    
                    card.used_count += 1
                
                card.save()
                
                # 更新API密钥使用统计
                api_key_obj.usage_count += 1
                api_key_obj.last_used_at = timezone.now()
                api_key_obj.save()
                
                # 构建成功响应数据
                data = {
                    'card_type': card.card_type,
                    'expire_date': card.expire_date.isoformat() if card.expire_date else None,
                    'remaining_count': card.remaining_count if card.card_type == 'count' else None,
                    'device_binding': {
                        'device_id': device_binding.device_id if device_binding else None,
                        'is_new_device': device_binding_result.get('is_new_device', False) if device_id else False
                    } if device_id else None
                }
                
                return True, ApiResponse.success(data, '验证成功'), card
                
        except Exception as e:
            logger.error(f"卡密验证失败: {e}", exc_info=True)
            return False, ApiResponse.system_error(f"验证过程中发生错误"), None
    
    @staticmethod
    def _handle_device_binding(card, device_id, request):
        """处理设备绑定"""
        try:
            # 获取客户端IP
            ip_address = CardVerificationService._get_client_ip(request) if request else '127.0.0.1'
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:255] if request else ''
            
            device_binding, created = DeviceBinding.objects.get_or_create(
                card=card,
                device_id=device_id,
                defaults={
                    'ip_address': ip_address,
                    'device_name': user_agent
                }
            )
            
            if not created:
                # 更新最后活跃时间
                device_binding.last_active_time = timezone.now()
                device_binding.ip_address = ip_address
                device_binding.save()
            
            # 检查设备数量限制
            active_device_count = DeviceBinding.objects.filter(
                card=card,
                is_active=True
            ).count()

            if active_device_count > card.max_devices:
                # 如果是新创建的绑定，需要删除它
                if created:
                    device_binding.delete()
                return {
                    'success': False,
                    'response': ApiResponse.device_limit_exceeded(),
                    'device_binding': None
                }
            
            return {
                'success': True,
                'response': None,
                'device_binding': device_binding,
                'is_new_device': created
            }
            
        except Exception as e:
            logger.error(f"设备绑定处理失败: {e}", exc_info=True)
            return {
                'success': False,
                'response': ApiResponse.system_error("设备绑定失败"),
                'device_binding': None
            }
    
    @staticmethod
    def _get_client_ip(request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip


class CardQueryService:
    """卡密查询服务"""
    
    @staticmethod
    def query_card(api_key_obj, card_key):
        """
        查询卡密信息
        
        Args:
            api_key_obj: API密钥对象
            card_key: 卡密
            
        Returns:
            tuple: (success, response_data)
        """
        try:
            # 查找卡密
            card_key_hash = hashlib.sha1(card_key.encode()).hexdigest()
            try:
                card = Card.objects.get(card_key_hash=card_key_hash)
            except Card.DoesNotExist:
                return False, ApiResponse.card_not_found()
            
            # 获取设备绑定信息
            device_bindings = DeviceBinding.objects.filter(card=card, is_active=True)
            
            # 获取最近的验证记录
            recent_logs = VerificationLog.objects.filter(
                card=card
            ).order_by('-verification_time')[:10]
            
            # 构建响应数据
            data = {
                'card_info': {
                    'card_type': card.card_type,
                    'status': card.status,
                    'expire_date': card.expire_date.isoformat() if card.expire_date else None,
                    'total_count': card.total_count if card.card_type == 'count' else None,
                    'used_count': card.used_count if card.card_type == 'count' else None,
                    'remaining_count': card.remaining_count if card.card_type == 'count' else None,
                    'first_used_at': card.first_used_at.isoformat() if card.first_used_at else None,
                    'last_used_at': card.last_used_at.isoformat() if card.last_used_at else None,
                    'allow_multi_device': card.allow_multi_device,
                    'max_devices': card.max_devices,
                    'is_expired': card.is_expired
                },
                'device_bindings': [
                    {
                        'device_id': binding.device_id,
                        'device_name': binding.device_name,
                        'ip_address': binding.ip_address,
                        'first_bind_time': binding.first_bind_time.isoformat(),
                        'last_active_time': binding.last_active_time.isoformat()
                    }
                    for binding in device_bindings
                ],
                'recent_logs': [
                    {
                        'verification_time': log.verification_time.isoformat(),
                        'ip_address': log.ip_address,
                        'success': log.success,
                        'error_message': log.error_message
                    }
                    for log in recent_logs
                ]
            }
            
            return True, ApiResponse.success(data, '查询成功')
            
        except Exception as e:
            logger.error(f"卡密查询失败: {e}", exc_info=True)
            return False, ApiResponse.system_error("查询过程中发生错误")


class ApiStatsService:
    """API统计服务"""
    
    @staticmethod
    def get_api_stats(api_key_obj=None, days=7):
        """
        获取API统计信息
        
        Args:
            api_key_obj: API密钥对象（可选，为None时统计所有）
            days: 统计天数
            
        Returns:
            dict: 统计数据
        """
        try:
            # 基础查询
            queryset = ApiCallLog.objects.all()
            if api_key_obj:
                queryset = queryset.filter(api_key=api_key_obj)
            
            # 时间范围
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            period_queryset = queryset.filter(call_time__gte=start_date)
            
            # 基础统计
            total_calls = queryset.count()
            successful_calls = queryset.filter(success=True).count()
            failed_calls = total_calls - successful_calls
            success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0
            
            # 平均响应时间
            avg_response_time = queryset.aggregate(
                avg_time=Avg('response_time')
            )['avg_time'] or 0
            
            # 今日和本小时统计
            today = timezone.now().date()
            calls_today = queryset.filter(call_time__date=today).count()
            
            current_hour = timezone.now().replace(minute=0, second=0, microsecond=0)
            calls_this_hour = queryset.filter(call_time__gte=current_hour).count()
            
            # 按小时统计（最近24小时）
            hourly_stats = ApiStatsService._get_hourly_stats(period_queryset)
            
            # 按天统计
            daily_stats = ApiStatsService._get_daily_stats(period_queryset, days)
            
            # 按端点统计
            endpoint_stats = ApiStatsService._get_endpoint_stats(period_queryset)
            
            # 如果不是特定API密钥，还要统计top API密钥
            top_api_keys = []
            if not api_key_obj:
                top_api_keys = ApiStatsService._get_top_api_keys(period_queryset)
            
            return {
                'total_calls': total_calls,
                'successful_calls': successful_calls,
                'failed_calls': failed_calls,
                'success_rate': round(success_rate, 2),
                'avg_response_time': round(avg_response_time, 2),
                'calls_today': calls_today,
                'calls_this_hour': calls_this_hour,
                'hourly_stats': hourly_stats,
                'daily_stats': daily_stats,
                'endpoint_stats': endpoint_stats,
                'top_api_keys': top_api_keys
            }
            
        except Exception as e:
            logger.error(f"获取API统计失败: {e}", exc_info=True)
            return {}
    
    @staticmethod
    def _get_hourly_stats(queryset):
        """获取按小时统计"""
        # 实现按小时统计逻辑
        return []
    
    @staticmethod
    def _get_daily_stats(queryset, days):
        """获取按天统计"""
        # 实现按天统计逻辑
        return []
    
    @staticmethod
    def _get_endpoint_stats(queryset):
        """获取按端点统计"""
        return list(queryset.values('endpoint').annotate(
            count=Count('id'),
            success_count=Count('id', filter=Q(success=True)),
            avg_response_time=Avg('response_time')
        ).order_by('-count')[:10])
    
    @staticmethod
    def _get_top_api_keys(queryset):
        """获取使用最多的API密钥"""
        return list(queryset.values('api_key__name').annotate(
            count=Count('id'),
            success_count=Count('id', filter=Q(success=True))
        ).order_by('-count')[:10])


class LoggingService:
    """日志记录服务"""
    
    @staticmethod
    def log_verification(card, request, api_key, success, error_message='', device_binding=None):
        """记录验证日志"""
        try:
            VerificationLog.objects.create(
                card=card,
                device_binding=device_binding,
                ip_address=CardVerificationService._get_client_ip(request) if request else '127.0.0.1',
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500] if request else '',
                success=success,
                error_message=error_message[:1000],
                api_key=api_key
            )
        except Exception as e:
            logger.error(f"记录验证日志失败: {e}", exc_info=True)
