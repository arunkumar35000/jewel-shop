from django.urls import path
from . import views

urlpatterns = [
    # Customer Catalog
    path('', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('detail/<slug:slug>/', views.product_detail, name='product_detail'),

    # Admin CRUD Operations
    path('manage/products/', views.admin_product_list, name='admin_product_list'),
    path('manage/products/create/', views.admin_product_create, name='admin_product_create'),
    path('manage/products/<int:pk>/edit/', views.admin_product_edit, name='admin_product_edit'),
    path('manage/products/<int:pk>/delete/', views.admin_product_delete, name='admin_product_delete'),
    path('manage/products/<int:pk>/360/', views.admin_360_upload, name='admin_360_upload'),
    path('manage/360-frame/<int:frame_id>/delete/', views.admin_delete_360_frame, name='admin_delete_360_frame'),

    # Admin Category Operations
    path('manage/categories/', views.admin_category_list, name='admin_category_list'),
    path('manage/categories/create/', views.admin_category_create, name='admin_category_create'),
    path('manage/categories/<int:pk>/edit/', views.admin_category_edit, name='admin_category_edit'),
    path('manage/categories/<int:pk>/delete/', views.admin_category_delete, name='admin_category_delete'),
]

