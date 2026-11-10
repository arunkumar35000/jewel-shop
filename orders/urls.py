from django.urls import path
from . import views
from backend_api.payment import stripe_mock_checkout_view

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('confirmed/<str:order_number>/', views.order_confirmation_view, name='order_confirmation'),
    path('payment/stripe/mock-checkout/<str:order_number>/', stripe_mock_checkout_view, name='stripe_mock_checkout'),
    path('history/', views.order_history_view, name='order_history'),
    path('detail/<str:order_number>/', views.order_detail_view, name='order_detail'),
    path('track/<str:order_number>/', views.order_tracking_view, name='order_tracking'),
    path('invoice/<str:order_number>/', views.invoice_view, name='order_invoice'),
    path('cancel/<str:order_number>/', views.order_cancel_view, name='order_cancel'),
]
