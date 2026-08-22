from . import views
from django.urls import path, include
from django.conf import settings
app_name = 'RE'
urlpatterns = [
    path("referral/", views.referral, name="referral"),
]   