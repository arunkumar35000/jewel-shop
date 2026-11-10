from django.urls import path
from . import views
from . import payment

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
    # STRIPE PAYMENT & TRANSACTIONS REST APIS
    # -------------------------------------------------------------
    path('payment/stripe/create-checkout-session/', payment.CreateStripePaymentAPIView.as_view(), name='api_stripe_create_session'),
    path('payment/stripe/success/', payment.StripePaymentSuccessView.as_view(), name='api_stripe_success'),
    path('payment/stripe/cancel/', payment.StripePaymentCancelView.as_view(), name='api_stripe_cancel'),
    path('payment/stripe/webhook/', payment.StripeWebhookAPIView.as_view(), name='api_stripe_webhook'),
    path('payment/transactions/', payment.TransactionListAPIView.as_view(), name='api_transactions_list'),

    # -------------------------------------------------------------
    # ADMIN PANEL COMMUNICATION REST APIS
    # -------------------------------------------------------------
    path('admin/dashboard-stats/', views.AdminDashboardStatsAPI.as_view(), name='api_admin_dashboard_stats'),
    path('admin/orders/', views.AdminOrderListAPI.as_view(), name='api_admin_orders'),
    path('admin/orders/<str:order_number>/status/', views.AdminOrderStatusUpdateAPI.as_view(), name='api_admin_order_status'),
    path('admin/customers/', views.AdminCustomerListAPI.as_view(), name='api_admin_customers'),
]
