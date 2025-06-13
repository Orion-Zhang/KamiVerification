from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='index'),
    path('stats/', views.StatsView.as_view(), name='stats'),
    path('charts/card-usage/', views.CardUsageChartView.as_view(), name='card_usage_chart'),
    path('charts/api-calls/', views.ApiCallsChartView.as_view(), name='api_calls_chart'),
]
