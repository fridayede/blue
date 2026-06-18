from django.urls import path
from . import views

app_name ='Task'

urlpatterns = [
    path('hometask/',views.hometask, name='hometask'),  
    path("task/<int:id>/", views.task, name="task"),
    path('complect/', views.complect, name='complect'), 
    
]
# path('details/<int:product_id>/',views.product_detail, name="product_detail")