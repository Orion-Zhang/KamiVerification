from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from cards.models import Card, VerificationLog
from api.models import ApiKey, ApiCallLog
from accounts.models import CustomUser
from accounts.mixins import ApprovedUserRequiredMixin


class DashboardView(ApprovedUserRequiredMixin, TemplateView):
    """控制面板主页"""
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 基础统计数据
        context.update({
            'total_cards': Card.objects.count(),
            'active_cards': Card.objects.filter(status='active').count(),
            'expired_cards': Card.objects.filter(status='expired').count(),
            'total_api_keys': ApiKey.objects.count(),
            'active_api_keys': ApiKey.objects.filter(is_active=True).count(),
        })

        # 只有超级管理员才能看到用户管理相关统计
        if self.request.user.is_superuser:
            context.update({
                'total_users': CustomUser.objects.count(),
                'pending_users': CustomUser.objects.filter(status='pending').count(),
            })
        else:
            context.update({
                'total_users': 0,
                'pending_users': 0,
            })

        # 今日统计
        today = timezone.now().date()
        context.update({
            'today_verifications': VerificationLog.objects.filter(
                verification_time__date=today
            ).count(),
            'today_api_calls': ApiCallLog.objects.filter(
                call_time__date=today
            ).count(),
        })

        # 最近7天的验证趋势
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_verifications = VerificationLog.objects.filter(
            verification_time__gte=seven_days_ago
        ).values('verification_time__date').annotate(
            count=Count('id')
        ).order_by('verification_time__date')

        context['recent_verifications'] = list(recent_verifications)

        # 最近的验证记录
        context['recent_logs'] = VerificationLog.objects.select_related(
            'card', 'device_binding'
        ).order_by('-verification_time')[:10]

        return context


class StatsView(ApprovedUserRequiredMixin, TemplateView):
    """统计页面"""
    template_name = 'dashboard/stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 卡密类型统计
        card_type_stats = Card.objects.values('card_type').annotate(
            count=Count('id')
        )
        context['card_type_stats'] = list(card_type_stats)

        # 卡密状态统计
        card_status_stats = Card.objects.values('status').annotate(
            count=Count('id')
        )
        context['card_status_stats'] = list(card_status_stats)

        # API调用统计
        api_call_stats = ApiCallLog.objects.values('success').annotate(
            count=Count('id')
        )
        context['api_call_stats'] = list(api_call_stats)

        return context


class CardUsageChartView(ApprovedUserRequiredMixin, TemplateView):
    """卡密使用图表数据"""

    def get(self, request, *args, **kwargs):
        # 获取最近30天的数据
        thirty_days_ago = timezone.now() - timedelta(days=30)

        # 按日期统计验证次数
        daily_usage = VerificationLog.objects.filter(
            verification_time__gte=thirty_days_ago
        ).extra(
            select={'day': 'date(verification_time)'}
        ).values('day').annotate(
            total=Count('id'),
            success=Count('id', filter=Q(success=True))
        ).order_by('day')

        # 格式化数据
        labels = []
        total_data = []
        success_data = []

        for item in daily_usage:
            labels.append(item['day'].strftime('%m-%d'))
            total_data.append(item['total'])
            success_data.append(item['success'])

        return JsonResponse({
            'labels': labels,
            'datasets': [
                {
                    'label': '总验证次数',
                    'data': total_data,
                    'borderColor': 'rgb(54, 162, 235)',
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'tension': 0.1
                },
                {
                    'label': '成功验证次数',
                    'data': success_data,
                    'borderColor': 'rgb(75, 192, 192)',
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'tension': 0.1
                }
            ]
        })


class ApiCallsChartView(ApprovedUserRequiredMixin, TemplateView):
    """API调用图表数据"""

    def get(self, request, *args, **kwargs):
        # 获取最近7天的数据
        seven_days_ago = timezone.now() - timedelta(days=7)

        # 按小时统计API调用
        hourly_calls = ApiCallLog.objects.filter(
            call_time__gte=seven_days_ago
        ).extra(
            select={'hour': 'strftime("%%Y-%%m-%%d %%H", call_time)'}
        ).values('hour').annotate(
            total=Count('id'),
            success=Count('id', filter=Q(success=True))
        ).order_by('hour')

        # 格式化数据
        labels = []
        total_data = []
        success_data = []

        for item in hourly_calls:
            labels.append(item['hour'])
            total_data.append(item['total'])
            success_data.append(item['success'])

        return JsonResponse({
            'labels': labels,
            'datasets': [
                {
                    'label': 'API调用总数',
                    'data': total_data,
                    'borderColor': 'rgb(255, 99, 132)',
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'tension': 0.1
                },
                {
                    'label': '成功调用数',
                    'data': success_data,
                    'borderColor': 'rgb(75, 192, 192)',
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'tension': 0.1
                }
            ]
        })
