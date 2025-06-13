from django.urls import path
from . import views

app_name = 'cards'

urlpatterns = [
    path('', views.CardListView.as_view(), name='list'),
    path('create/', views.CardCreateView.as_view(), name='create'),
    path('batch-create/', views.BatchCreateView.as_view(), name='batch_create'),
    path('<int:pk>/', views.CardDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.CardUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.CardDeleteView.as_view(), name='delete'),
    path('<int:pk>/toggle-status/', views.toggle_card_status, name='toggle_card_status'),
    path('<int:pk>/unbind-device/', views.UnbindDeviceView.as_view(), name='unbind_device'),
    path('export/', views.ExportCardsView.as_view(), name='export'),
    path('verification-logs/', views.VerificationLogListView.as_view(), name='verification_logs'),
]
