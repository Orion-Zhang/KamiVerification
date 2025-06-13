from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomAuthenticationForm(AuthenticationForm):
    """自定义登录表单，添加Bootstrap样式"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 为用户名字段添加样式
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '请输入用户名'
        })
        
        # 为密码字段添加样式
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '请输入密码'
        })


class CustomUserCreationForm(UserCreationForm):
    """自定义注册表单"""
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 为所有字段添加Bootstrap样式
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control'
            })
            
        # 设置占位符
        self.fields['username'].widget.attrs['placeholder'] = '请输入用户名'
        self.fields['email'].widget.attrs['placeholder'] = '请输入邮箱地址'
        self.fields['phone'].widget.attrs['placeholder'] = '请输入手机号码（可选）'
        self.fields['password1'].widget.attrs['placeholder'] = '请输入密码'
        self.fields['password2'].widget.attrs['placeholder'] = '请再次输入密码'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data.get('phone', '')
        if commit:
            user.save()
        return user
