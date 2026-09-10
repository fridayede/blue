from .import views
from django.urls import path


app_name ="Swap"
urlpatterns = [
    path('swappage/', views.swappage, name='swappage'),
]
