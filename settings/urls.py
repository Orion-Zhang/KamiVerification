from django.urls import path
from . import views

app_name = 'settings'

urlpatterns = [
    path('', views.settings_view, name='index'),
    path('upload-image/', views.upload_image, name='upload_image'),
    path('delete-image/', views.delete_image, name='delete_image'),
]
