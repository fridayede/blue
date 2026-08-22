from django.urls import path
from .import views


app_name = 'Withdraw'
urlpatterns = [
    path('withdraw/', views.withdraw, name='withdraw')
]