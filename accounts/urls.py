from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='customer_profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    
    # Addresses
    path('addresses/', views.address_list_view, name='address_list'),
    path('addresses/add/', views.address_create_view, name='address_create'),
    path('addresses/<int:address_id>/edit/', views.address_edit_view, name='address_edit'),
    path('addresses/<int:address_id>/delete/', views.address_delete_view, name='address_delete'),
    
    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist_view'),
    path('wishlist/toggle/<int:product_id>/', views.wishlist_toggle_api, name='wishlist_toggle_api'),
    path('wishlist/move-to-cart/<int:product_id>/', views.wishlist_move_to_cart, name='wishlist_move_to_cart'),
]

