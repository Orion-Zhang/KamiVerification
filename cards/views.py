from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.db import transaction
from django.utils import timezone
from django import forms
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import uuid
import hashlib
import pandas as pd
from io import BytesIO
import logging
from .models import Card, DeviceBinding, VerificationLog
from accounts.mixins import ApprovedUserRequiredMixin

logger = logging.getLogger(__name__)


def generate_unique_card_key():
    """生成唯一的卡密"""
    max_attempts = 10
    for attempt in range(max_attempts):
        card_key = str(uuid.uuid4()).replace('-', '')
        card_key_hash = hashlib.sha1(card_key.encode()).hexdigest()

        # 检查是否已存在
        if not Card.objects.filter(card_key_hash=card_key_hash).exists():
            return card_key

    # 如果10次尝试都失败，使用时间戳确保唯一性
    import time
    return str(uuid.uuid4()).replace('-', '') + str(int(time.time() * 1000000))[-6:]


class CardForm(forms.ModelForm):
    """卡密表单"""
    class Meta:
        model = Card
        fields = ['card_type', 'valid_days', 'expire_date', 'total_count',
                 'allow_multi_device', 'max_devices', 'note']
        widgets = {
            'card_type': forms.Select(attrs={'class': 'form-select'}),
            'valid_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'expire_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'total_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'allow_multi_device': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'max_devices': forms.NumberInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['expire_date'].required = False
        self.fields['valid_days'].required = False
        self.fields['total_count'].required = False


class BatchCreateForm(forms.Form):
    """批量创建表单"""
    card_type = forms.ChoiceField(
        choices=Card.CARD_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_card_type'})
    )
    count = forms.IntegerField(
        min_value=1, max_value=1000,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_count'})
    )
    valid_days = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_valid_days'})
    )
    total_count = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_total_count'})
    )
    allow_multi_device = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_allow_multi_device'})
    )
    max_devices = forms.IntegerField(
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_max_devices'})
    )


class CardListView(ApprovedUserRequiredMixin, ListView):
    """卡密列表视图"""
    model = Card
    template_name = 'cards/list.html'
    context_object_name = 'cards'
    paginate_by = 20

    def get_queryset(self):
        queryset = Card.objects.select_related('created_by').order_by('-created_at')

        # 搜索功能
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(card_key__icontains=search) |
                Q(note__icontains=search) |
                Q(created_by__username__icontains=search)
            )

        # 筛选功能
        card_type = self.request.GET.get('card_type')
        if card_type:
            queryset = queryset.filter(card_type=card_type)

        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['card_type'] = self.request.GET.get('card_type', '')
        context['status'] = self.request.GET.get('status', '')
        context['card_type_choices'] = Card.CARD_TYPE_CHOICES
        context['status_choices'] = Card.STATUS_CHOICES
        return context


class CardCreateView(ApprovedUserRequiredMixin, CreateView):
    """创建卡密视图"""
    model = Card
    form_class = CardForm
    template_name = 'cards/create.html'
    success_url = reverse_lazy('cards:list')

    def form_valid(self, form):
        # 生成唯一卡密
        card_key = generate_unique_card_key()
        form.instance.card_key = card_key
        form.instance.created_by = self.request.user

        # 设置过期时间
        if form.instance.card_type == 'time' and form.instance.valid_days:
            form.instance.expire_date = timezone.now() + timezone.timedelta(days=form.instance.valid_days)

        messages.success(self.request, f'卡密创建成功！卡密：{card_key}')
        return super().form_valid(form)


class BatchCreateView(ApprovedUserRequiredMixin, TemplateView):
    """批量创建卡密视图"""
    template_name = 'cards/batch_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BatchCreateForm()
        return context

    def post(self, request, *args, **kwargs):
        form = BatchCreateForm(request.POST)
        if form.is_valid():
            cards = []
            created_keys = set()  # 用于检查本次批量创建中的重复

            for i in range(form.cleaned_data['count']):
                # 生成唯一的卡密
                max_attempts = 10
                for attempt in range(max_attempts):
                    card_key = generate_unique_card_key()

                    # 检查是否与本次批量创建中的其他卡密重复
                    if card_key not in created_keys:
                        created_keys.add(card_key)
                        break
                else:
                    # 如果10次尝试都失败，使用序号确保唯一性
                    import time
                    card_key = str(uuid.uuid4()).replace('-', '') + f"{int(time.time() * 1000000)}{i:04d}"[-10:]
                    created_keys.add(card_key)

                card = Card(
                    card_key=card_key,
                    card_key_hash=hashlib.sha1(card_key.encode()).hexdigest(),  # 手动设置哈希值
                    card_type=form.cleaned_data['card_type'],
                    created_by=request.user
                )

                if form.cleaned_data['card_type'] == 'time' and form.cleaned_data['valid_days']:
                    card.valid_days = form.cleaned_data['valid_days']
                    card.expire_date = timezone.now() + timezone.timedelta(days=form.cleaned_data['valid_days'])
                elif form.cleaned_data['card_type'] == 'count' and form.cleaned_data['total_count']:
                    card.total_count = form.cleaned_data['total_count']

                card.allow_multi_device = form.cleaned_data['allow_multi_device']
                card.max_devices = form.cleaned_data['max_devices']
                cards.append(card)

            try:
                with transaction.atomic():
                    Card.objects.bulk_create(cards)
                messages.success(request, f'成功批量创建 {len(cards)} 个卡密！')
                return redirect('cards:list')
            except Exception as e:
                messages.error(request, f'批量创建失败：{str(e)}')
                return self.render_to_response({'form': form})

        return self.render_to_response({'form': form})


class CardDetailView(ApprovedUserRequiredMixin, DetailView):
    """卡密详情视图"""
    model = Card
    template_name = 'cards/detail.html'
    context_object_name = 'card'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        card = self.get_object()

        # 获取设备绑定信息
        context['device_bindings'] = DeviceBinding.objects.filter(
            card=card
        ).order_by('-last_active_time')

        # 获取验证记录
        context['verification_logs'] = VerificationLog.objects.filter(
            card=card
        ).order_by('-verification_time')[:20]

        return context


class CardUpdateView(ApprovedUserRequiredMixin, UpdateView):
    """编辑卡密视图"""
    model = Card
    form_class = CardForm
    template_name = 'cards/edit.html'

    def get_success_url(self):
        return reverse_lazy('cards:detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, '卡密信息更新成功！')
        return super().form_valid(form)


class CardDeleteView(ApprovedUserRequiredMixin, DeleteView):
    """删除卡密视图"""
    model = Card
    template_name = 'cards/delete.html'
    success_url = reverse_lazy('cards:list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, '卡密删除成功！')
        return super().delete(request, *args, **kwargs)


class UnbindDeviceView(ApprovedUserRequiredMixin, TemplateView):
    """解绑设备视图"""

    def get(self, request, pk):
        """处理GET请求，从URL参数获取device_id并执行解绑"""
        card = get_object_or_404(Card, pk=pk)
        device_id = request.GET.get('device_id')

        if device_id:
            # 检查设备绑定是否存在
            binding = DeviceBinding.objects.filter(card=card, device_id=device_id).first()
            if binding:
                binding.delete()
                messages.success(request, '设备解绑成功！')
            else:
                messages.error(request, '未找到该设备绑定记录！')
        else:
            messages.error(request, '设备ID不能为空！')

        return redirect('cards:detail', pk=pk)

    def post(self, request, pk):
        """处理POST请求，从表单数据获取device_id并执行解绑"""
        card = get_object_or_404(Card, pk=pk)
        device_id = request.POST.get('device_id')

        if device_id:
            # 检查设备绑定是否存在
            binding = DeviceBinding.objects.filter(card=card, device_id=device_id).first()
            if binding:
                binding.delete()
                messages.success(request, '设备解绑成功！')
            else:
                messages.error(request, '未找到该设备绑定记录！')
        else:
            messages.error(request, '设备ID不能为空！')

        return redirect('cards:detail', pk=pk)


class ExportCardsView(ApprovedUserRequiredMixin, TemplateView):
    """导出卡密视图"""

    def get(self, request):
        # 获取筛选参数
        card_type = request.GET.get('card_type')
        status = request.GET.get('status')

        queryset = Card.objects.select_related('created_by').order_by('-created_at')

        if card_type:
            queryset = queryset.filter(card_type=card_type)
        if status:
            queryset = queryset.filter(status=status)

        # 准备数据
        data = []
        for card in queryset:
            data.append({
                '卡密': card.card_key,
                '类型': card.get_card_type_display(),
                '状态': card.get_status_display(),
                '有效天数': card.valid_days if card.card_type == 'time' else '',
                '过期时间': card.expire_date.strftime('%Y-%m-%d %H:%M:%S') if card.expire_date else '',
                '总次数': card.total_count if card.card_type == 'count' else '',
                '已使用次数': card.used_count if card.card_type == 'count' else '',
                '允许多设备': '是' if card.allow_multi_device else '否',
                '最大设备数': card.max_devices,
                '创建者': card.created_by.username,
                '创建时间': card.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                '备注': card.note,
            })

        # 创建Excel文件
        df = pd.DataFrame(data)
        output = BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='卡密列表', index=False)

        output.seek(0)

        # 返回文件
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="cards_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'

        return response


class VerificationLogListView(ApprovedUserRequiredMixin, ListView):
    """验证记录列表视图"""
    model = VerificationLog
    template_name = 'cards/verification_logs.html'
    context_object_name = 'logs'
    paginate_by = 50

    def get_queryset(self):
        queryset = VerificationLog.objects.select_related(
            'card', 'device_binding'
        ).order_by('-verification_time')

        # 搜索功能
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(card__card_key__icontains=search) |
                Q(ip_address__icontains=search) |
                Q(api_key__icontains=search)
            )

        # 筛选功能
        success = self.request.GET.get('success')
        if success:
            queryset = queryset.filter(success=success == 'true')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['success'] = self.request.GET.get('success', '')
        return context


@csrf_exempt
@require_http_methods(["POST"])
def toggle_card_status(request, pk):
    """切换卡密状态"""
    try:
        # 检查用户权限
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)

        card = get_object_or_404(Card, pk=pk)

        # 检查权限：只有创建者或超级用户可以修改
        if card.created_by != request.user and not request.user.is_superuser:
            return JsonResponse({'success': False, 'message': '没有权限修改此卡密'}, status=403)

        # 切换状态：只在active和inactive之间切换
        if card.status == 'active':
            card.status = 'inactive'
            action = "禁用"
        elif card.status == 'inactive':
            card.status = 'active'
            action = "启用"
        else:
            return JsonResponse({'success': False, 'message': '此卡密状态无法切换'}, status=400)

        card.save()

        # 记录操作日志
        logger.info(f"用户 {request.user.username} {action}了卡密 {card.card_key[:8]}***")

        return JsonResponse({
            'success': True,
            'message': f'卡密已{action}',
            'new_status': card.status,
            'status_text': card.get_status_display()
        })

    except Exception as e:
        logger.error(f"切换卡密状态失败: {e}", exc_info=True)
        return JsonResponse({'success': False, 'message': '操作失败，请重试'}, status=500)
