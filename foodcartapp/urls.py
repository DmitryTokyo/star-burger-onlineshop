from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views


app_name = "foodcartapp"

urlpatterns = [
    path('products/', views.product_list_api),
    path('banners/start-page-header/', views.banners_list_api),
    path('order/', views.register_order),
    path('order/<int:pk>/', views.handle_order_detail),
]
