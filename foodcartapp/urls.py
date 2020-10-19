from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import product_list_api, banners_list_api, register_order


app_name = "foodcartapp"

urlpatterns = [
    path('products/', product_list_api),
    path('banners/start-page-header/', banners_list_api),
    path('order/', register_order),
]
