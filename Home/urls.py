from django.urls import path
from . import views

app_name ='Home'


urlpatterns = [
    path('clam/',views.clam, name='clam'),
]
