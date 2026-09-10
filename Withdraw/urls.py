from django.urls import path
from .import views


app_name = 'Withdraw'
urlpatterns = [
    path('withdraw/', views.withdraw, name='withdraw'),
    path('withdraw-health-check/', views.withdraw_health_check, name='withdraw_health_check'),
]