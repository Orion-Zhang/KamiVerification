from django.urls import path, include
from . import views

app_name = 'api'

# API接口路由
api_patterns = [
    path('verify/', views.VerifyCardView.as_view(), name='verify'),
    path('query/', views.QueryCardView.as_view(), name='query'),
    path('health/', views.health_check, name='health_check'),
    path('stats/', views.ApiStatsView.as_view(), name='stats'),
]

# 管理页面路由
management_patterns = [
    path('keys/', views.ApiKeyListView.as_view(), name='key_list'),
    path('keys/create/', views.ApiKeyCreateView.as_view(), name='key_create'),
    path('keys/<int:pk>/edit/', views.ApiKeyUpdateView.as_view(), name='key_edit'),
    path('keys/<int:pk>/delete/', views.ApiKeyDeleteView.as_view(), name='key_delete'),
    path('keys/<int:pk>/toggle-status/', views.toggle_api_key_status, name='toggle_api_key_status'),
    path('logs/', views.ApiCallLogListView.as_view(), name='call_logs'),
]

urlpatterns = api_patterns + management_patterns
