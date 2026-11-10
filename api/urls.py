from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.ProductListAPI.as_view(), name='api_product_list'),
    path('products/<slug:slug>/', views.ProductDetailAPI.as_view(), name='api_product_detail'),
    path('products/<slug:slug>/360-frames/', views.Product360FramesAPI.as_view(), name='api_product_360_frames'),
    path('cart/', views.CartAPI.as_view(), name='api_cart'),
    path('custom-orders/', views.CustomOrderListCreateAPI.as_view(), name='api_custom_orders'),
]

