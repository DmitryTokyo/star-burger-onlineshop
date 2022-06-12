from django.urls import path

from foodcartapp import views


app_name = 'foodcartapp'

urlpatterns = [
    path('products/', views.ProductsListApiViews.as_view(), name='product_list'),
    path('banners/', views.BannersListViews.as_view(), name='banners_list'),
    path('order/', views.RegisterOrderViews.as_view(), name='register_order'),
    path('order/<int:pk>/', views.OrderDetailsView.as_view(), name='handle_order'),
]
