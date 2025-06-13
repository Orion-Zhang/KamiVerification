from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import CreateView, TemplateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django import forms
from .models import CustomUser, LoginLog
from .forms import CustomAuthenticationForm
from .mixins import ApprovedUserRequiredMixin


class CustomUserCreationForm(UserCreationForm):
    """自定义用户注册表单"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '邮箱地址'})
    )
    phone = forms.CharField(
        max_length=11,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '手机号码'})
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '用户名'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': '密码'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': '确认密码'})


class RegisterView(CreateView):
    """用户注册视图"""
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:pending')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            '注册成功！您的账户正在等待管理员审批，审批通过后即可登录。'
        )
        return response


class PendingApprovalView(TemplateView):
    """等待审批页面"""
    template_name = 'accounts/pending.html'


class CustomLoginView(LoginView):
    """自定义登录视图"""
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        """登录成功后的处理"""
        user = form.get_user()

        # 检查用户是否可以访问控制面板
        if not user.can_access_dashboard():
            messages.error(self.request, '您的账户尚未通过审批，请等待管理员审批。')
            return redirect('accounts:pending')

        response = super().form_valid(form)
        messages.success(self.request, f'欢迎回来，{self.request.user.username}！')
        return response


class CustomLogoutView(LogoutView):
    """自定义注销视图"""
    template_name = 'registration/logged_out.html'

    def dispatch(self, request, *args, **kwargs):
        """处理注销请求"""
        if request.user.is_authenticated:
            username = request.user.username
            messages.success(request, f'再见，{username}！您已成功退出登录。')
        return super().dispatch(request, *args, **kwargs)


class ProfileView(ApprovedUserRequiredMixin, UpdateView):
    """个人资料页面"""
    model = CustomUser
    fields = ['email', 'phone']
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, '个人资料更新成功！')
        return super().form_valid(form)
