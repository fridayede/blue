from .import views
from django.urls import path

app_name = 'Withdrawblue'


urlpatterns = [
    path('withdrawblue/', views.withdrawblue, name='withdrawblue'), 
]