import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jewellery_shop.settings')
import django
django.setup()

from django.test import Client
from django.urls import reverse
from products.models import Product, Category
from custom_orders.models import CustomOrder
from orders.models import Order
from django.contrib.auth.models import User

client = Client()

print("=" * 65)
print("AURA LUXURY JEWELLERY - ENDPOINT & INTEGRATION VERIFICATION")
print("=" * 65)

endpoints = [
    ('Homepage', reverse('home')),
    ('About Us', reverse('about')),
    ('Contact Concierge', reverse('contact')),
    ('Product Catalog', reverse('product_list')),
    ('Shopping Bag', reverse('cart_detail')),
    ('Customer Login', reverse('login')),
    ('Customer Register', reverse('register')),
    ('Custom Studio Request Form', reverse('custom_order_create')),
    ('API Product List', reverse('api_product_list')),
    ('API Cart View', reverse('api_cart')),
]

# Check public endpoints
for name, url in endpoints:
    resp = client.get(url)
    assert resp.status_code == 200, f"Failed on {name} ({url}) with status {resp.status_code}"
    print(f"[✓] {name:<28} -> {url:<28} (HTTP 200 OK)")

# Check product detail view & 360 frames
first_product = Product.objects.first()
if first_product:
    detail_url = reverse('product_detail', kwargs={'slug': first_product.slug})
    resp = client.get(detail_url)
    assert resp.status_code == 200
    print(f"[✓] {'Product Detail Page':<28} -> {detail_url:<28} (HTTP 200 OK)")
    print(f"    - Name: '{first_product.name}' | SKU: {first_product.sku}")
    print(f"    - Has 360° Sequence: {first_product.has_360} ({first_product.count_360_frames} actual frames)")

    api_360_url = reverse('api_product_360_frames', kwargs={'slug': first_product.slug})
    resp_360 = client.get(api_360_url)
    assert resp_360.status_code == 200
    print(f"[✓] {'API 360° Frames':<28} -> {api_360_url:<28} (HTTP 200 OK)")

# Check Customer logged in views
client.login(username='customer', password='Customer@123')
auth_endpoints = [
    ('Customer Profile', reverse('customer_profile')),
    ('Saved Addresses', reverse('address_list')),
    ('Wishlist View', reverse('wishlist_view')),
    ('Order History', reverse('order_history')),
    ('Custom Requests Track', reverse('customer_custom_orders')),
]
for name, url in auth_endpoints:
    resp = client.get(url)
    assert resp.status_code == 200, f"Failed on {name} ({url}) with status {resp.status_code}"
    print(f"[✓] {name:<28} -> {url:<28} (HTTP 200 OK)")

# Check Order Detail and Invoice
demo_order = Order.objects.first()
if demo_order:
    order_detail_url = reverse('order_detail', kwargs={'order_number': demo_order.order_number})
    resp = client.get(order_detail_url)
    assert resp.status_code == 200
    print(f"[✓] {'Order Detail Page':<28} -> {order_detail_url:<28} (HTTP 200 OK)")

    tracking_url = reverse('order_tracking', kwargs={'order_number': demo_order.order_number})
    resp = client.get(tracking_url)
    assert resp.status_code == 200
    print(f"[✓] {'Order Tracking Page':<28} -> {tracking_url:<28} (HTTP 200 OK)")

    invoice_url = reverse('order_invoice', kwargs={'order_number': demo_order.order_number})
    resp = client.get(invoice_url)
    assert resp.status_code == 200
    print(f"[✓] {'GST Tax Invoice':<28} -> {invoice_url:<28} (HTTP 200 OK)")

# Check Custom Order Detail
demo_custom = CustomOrder.objects.first()
if demo_custom:
    custom_detail_url = reverse('customer_custom_order_detail', kwargs={'request_id': demo_custom.request_id})
    resp = client.get(custom_detail_url)
    assert resp.status_code == 200
    print(f"[✓] {'Custom Order Detail':<28} -> {custom_detail_url:<28} (HTTP 200 OK)")

# Check Admin Logged in views
client.login(username='admin', password='Admin@123')
admin_endpoints = [
    ('Admin Dashboard', reverse('admin_dashboard')),
    ('Admin Product List', reverse('admin_product_list')),
    ('Admin Product Create Form', reverse('admin_product_create')),
    ('Admin Category List', reverse('admin_category_list')),
    ('Admin Orders List', reverse('admin_orders_list')),
    ('Admin Custom Requests', reverse('admin_custom_requests_list')),
    ('Admin Customer Directory', reverse('admin_customers_list')),
]
for name, url in admin_endpoints:
    resp = client.get(url)
    assert resp.status_code == 200, f"Failed on {name} ({url}) with status {resp.status_code}"
    print(f"[✓] {name:<28} -> {url:<28} (HTTP 200 OK)")

print("=" * 65)
print("ALL 25+ VIEWS AND API ENDPOINTS VERIFIED SUCCESSFULLY WITH HTTP 200!")
print("=" * 65)

