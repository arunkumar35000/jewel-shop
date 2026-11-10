from django.urls import path
from . import views

urlpatterns = [
    # -------------------------------------------------------------
    # WEBSITE CLIENT-FACING REST APIS
    # -------------------------------------------------------------
    path('categories/', views.CategoryListAPI.as_view(), name='api_categories'),
    path('products/', views.ProductListAPI.as_view(), name='api_product_list'),
    path('products/<slug:slug>/', views.ProductDetailAPI.as_view(), name='api_product_detail'),
    path('products/<slug:slug>/360-frames/', views.Product360FramesAPI.as_view(), name='api_product_360_frames'),
    path('cart/', views.CartAPI.as_view(), name='api_cart'),
    path('cart/add/', views.CartItemAddAPI.as_view(), name='api_cart_add'),
    path('orders/track/<str:order_number>/', views.OrderTrackAPI.as_view(), name='api_order_track'),
    path('custom-orders/', views.CustomOrderListCreateAPI.as_view(), name='api_custom_orders'),

    # -------------------------------------------------------------
    # ADMIN PANEL COMMUNICATION REST APIS
    # -------------------------------------------------------------
    path('admin/dashboard-stats/', views.AdminDashboardStatsAPI.as_view(), name='api_admin_dashboard_stats'),
    path('admin/orders/', views.AdminOrderListAPI.as_view(), name='api_admin_orders'),
    path('admin/orders/<str:order_number>/status/', views.AdminOrderStatusUpdateAPI.as_view(), name='api_admin_order_status'),
    path('admin/customers/', views.AdminCustomerListAPI.as_view(), name='api_admin_customers'),
]
