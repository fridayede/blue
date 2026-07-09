from django.urls import path
from . import views

app_name ='Task'

urlpatterns = [
    path('hometask/',views.hometask, name='hometask'),  
    path("task/<int:id>/", views.task, name="task"),
    path('complect/', views.complect, name='complect'),
    # path('ad-token/', views.request_ad_token, name='ad_token'),
       path('get-ad-token/', views.request_ad_token, name='get_ad_token'),
    path('adsgram-postback/', views.adsgram_postback, name='adsgram_postback'),
   
    path('point/', views.point, name='point'),
    
]
# path('details/<int:product_id>/',views.product_detail, name="product_detail")