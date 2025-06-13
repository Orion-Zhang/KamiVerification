from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import SystemSettings
from .forms import SystemSettingsForm
from accounts.mixins import superuser_required


def is_superuser(user):
    """检查用户是否为超级用户"""
    return user.is_superuser


@superuser_required
def settings_view(request):
    """系统设置页面"""
    settings = SystemSettings.get_settings()

    if request.method == 'POST':
        form = SystemSettingsForm(request.POST, request.FILES, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, '系统设置已成功更新！')
            return redirect('settings:index')
        else:
            messages.error(request, '设置更新失败，请检查输入的信息。')
    else:
        form = SystemSettingsForm(instance=settings)

    context = {
        'form': form,
        'settings': settings,
    }
    return render(request, 'settings/index.html', context)


@require_http_methods(["POST"])
@superuser_required
def upload_image(request):
    """AJAX图片上传"""
    if 'image' not in request.FILES:
        return JsonResponse({'success': False, 'error': '没有选择文件'})

    image = request.FILES['image']
    image_type = request.POST.get('type', 'hero')

    # 验证文件类型
    allowed_extensions = ['jpg', 'jpeg', 'png', 'svg', 'webp']
    if image_type == 'favicon':
        allowed_extensions = ['ico', 'png']

    file_extension = image.name.split('.')[-1].lower()
    if file_extension not in allowed_extensions:
        return JsonResponse({
            'success': False,
            'error': f'不支持的文件格式。支持的格式: {", ".join(allowed_extensions)}'
        })

    # 验证文件大小 (最大5MB)
    if image.size > 5 * 1024 * 1024:
        return JsonResponse({'success': False, 'error': '文件大小不能超过5MB'})

    try:
        settings = SystemSettings.get_settings()

        # 根据类型保存图片
        if image_type == 'hero':
            settings.hero_image = image
        elif image_type == 'logo':
            settings.logo_image = image
        elif image_type == 'favicon':
            settings.favicon = image
        else:
            return JsonResponse({'success': False, 'error': '无效的图片类型'})

        settings.save()

        # 返回图片URL
        if image_type == 'hero' and settings.hero_image:
            image_url = settings.hero_image.url
        elif image_type == 'logo' and settings.logo_image:
            image_url = settings.logo_image.url
        elif image_type == 'favicon' and settings.favicon:
            image_url = settings.favicon.url
        else:
            image_url = None

        return JsonResponse({
            'success': True,
            'image_url': image_url,
            'message': '图片上传成功！'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'上传失败: {str(e)}'})


@require_http_methods(["POST"])
@superuser_required
def delete_image(request):
    """删除图片"""
    image_type = request.POST.get('type')

    if image_type not in ['hero', 'logo', 'favicon']:
        return JsonResponse({'success': False, 'error': '无效的图片类型'})

    try:
        settings = SystemSettings.get_settings()

        if image_type == 'hero' and settings.hero_image:
            settings.hero_image.delete()
            settings.hero_image = None
        elif image_type == 'logo' and settings.logo_image:
            settings.logo_image.delete()
            settings.logo_image = None
        elif image_type == 'favicon' and settings.favicon:
            settings.favicon.delete()
            settings.favicon = None

        settings.save()

        return JsonResponse({'success': True, 'message': '图片已删除'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'删除失败: {str(e)}'})
