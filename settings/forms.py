from django import forms
from django.core.validators import RegexValidator
from .models import SystemSettings


class SystemSettingsForm(forms.ModelForm):
    """系统设置表单"""
    
    # 颜色验证器
    color_validator = RegexValidator(
        regex=r'^#[0-9A-Fa-f]{6}$',
        message='请输入有效的十六进制颜色代码，如 #3b82f6'
    )
    
    class Meta:
        model = SystemSettings
        fields = [
            'site_name', 'site_subtitle', 'site_description',
            'hero_image', 'logo_image', 'favicon',
            'primary_color', 'accent_color',
            'enable_registration', 'enable_api_docs', 'enable_statistics',
            'contact_email', 'contact_phone',
            'github_url', 'website_url',
            'maintenance_mode', 'maintenance_message'
        ]
        
        widgets = {
            'site_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '网站名称'
            }),
            'site_subtitle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '网站副标题'
            }),
            'site_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '网站描述'
            }),
            'hero_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'logo_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'favicon': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.ico,.png'
            }),
            'primary_color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'placeholder': '#3b82f6'
            }),
            'accent_color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'placeholder': '#06b6d4'
            }),
            'enable_registration': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'enable_api_docs': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'enable_statistics': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'admin@example.com'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+86 138 0000 0000'
            }),
            'github_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/username'
            }),
            'website_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.example.com'
            }),
            'maintenance_mode': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'maintenance_message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': '维护提示信息'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 添加颜色验证器
        self.fields['primary_color'].validators.append(self.color_validator)
        self.fields['accent_color'].validators.append(self.color_validator)
        
        # 设置必填字段
        self.fields['site_name'].required = True
        self.fields['site_subtitle'].required = True
        
        # 添加帮助文本
        self.fields['hero_image'].help_text = '推荐尺寸: 600x400px，支持 JPG、PNG、SVG、WebP 格式，最大5MB'
        self.fields['logo_image'].help_text = '推荐尺寸: 200x200px，支持 JPG、PNG、SVG、WebP 格式，最大5MB'
        self.fields['favicon'].help_text = '推荐尺寸: 32x32px，支持 ICO、PNG 格式，最大5MB'
        
    def clean_primary_color(self):
        """验证主色调"""
        color = self.cleaned_data.get('primary_color')
        if color and not color.startswith('#'):
            color = '#' + color
        return color
    
    def clean_accent_color(self):
        """验证强调色"""
        color = self.cleaned_data.get('accent_color')
        if color and not color.startswith('#'):
            color = '#' + color
        return color
