from django.urls import path
from . import views

urlpatterns = [
    path('', views.custom_order_create, name='custom_order_create'),
    path('success/<str:request_id>/', views.custom_order_success, name='custom_order_success'),
    path('my-requests/', views.customer_custom_orders, name='customer_custom_orders'),
    path('request/<str:request_id>/', views.customer_custom_order_detail, name='customer_custom_order_detail'),
    path('request/<str:request_id>/quote-respond/', views.quotation_respond, name='quotation_respond'),
]

