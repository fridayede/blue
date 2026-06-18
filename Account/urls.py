from django.urls import path
from . import views

app_name='Account'

urlpatterns = [
    path('login/', views.login,name='login'),
    path('register/', views.register,name='register'),
    path('verifyEmail/',views.verifyEmail,name='verifyEmail'),
    # path('massage/',views.massage,name='massage'),
    path('resetPassword/',views.resetPassword, name='resetPassword'),
    path('newPassword/',views.newPassword,name='newPassword'),
    path('logout/',views.logout,name='logout'),
]