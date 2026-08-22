from django.urls import path
from . import views

app_name ='Task'

urlpatterns = [
    path('hometask/',views.hometask, name='hometask'),  
    path("task/<int:id>/", views.task, name="task"),
    path('complect/', views.complect, name='complect'),
    # path('ad-token/', views.request_ad_token, name='ad_token'),
    path('get-ad-token/', views.request_ad_token, name='get_ad_token'),
    # path('adsgram-postback/', views.adsgram_postback, name='adsgram_postback'),
   path(
    "save-telegram-id/",
    views.save_telegram_id,
    name="save_telegram_id"
),
    path('point/', views.point, name='point'),
    # path('adsgram-postback/', views.adsgram_debug, name='adsgram_postback'),  
# new for monetag
     path('ad-status/', views.check_ad_status, name='check_ad_status'),

    # Register THIS exact URL in your Monetag dashboard's postback field
    path('monetag-postback/', views.monetag_postback, name='monetag_postback'),


# for adsgram
    path('get-ad-token/', views.requests_ad_token, name='get_ad_token'),
    path('adsgram-postback/', views.adsgram_postback, name='adsgram_postback'),
    path('ad-status/', views.ad_status, name='ad_status'),
path(
        "claim-adsgram-reward/",
        views.claim_adsgram_reward,
        name="claim_adsgram_reward",
    ),
    
]
# path('details/<int:product_id>/',views.product_detail, name="product_detail")