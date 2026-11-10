from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('orders/', views.admin_orders_list, name='admin_orders_list'),
    path('orders/<str:order_number>/', views.admin_order_detail, name='admin_order_detail'),
    path('custom-requests/', views.admin_custom_requests_list, name='admin_custom_requests_list'),
    path('custom-requests/<str:request_id>/', views.admin_custom_request_detail, name='admin_custom_request_detail'),
    path('custom-requests/<str:request_id>/quotation/', views.admin_quotation_create, name='admin_quotation_create'),
    path('customers/', views.admin_customers_list, name='admin_customers_list'),
    path('customers/<int:customer_id>/', views.admin_customer_detail, name='admin_customer_detail'),
]

