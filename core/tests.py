from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from products.models import Product, Category, ProductImage, Product360Image
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem
from custom_orders.models import CustomOrder, CustomOrderQuotation
from accounts.models import Address, Wishlist


class JewelleryECommerceTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create users
        self.admin = User.objects.create_superuser('admin_test', 'admin@test.com', 'AdminPass123')
        self.customer = User.objects.create_user('cust_test', 'cust@test.com', 'CustPass123', first_name='Ananya', last_name='Patel')
        
        # Create category
        self.category = Category.objects.create(
            name="Gold Necklaces",
            slug="gold-necklaces",
            description="Pure 22K gold necklaces"
        )
        
        # Create Product with flags
        self.product = Product.objects.create(
            name="22K Royal Temple Choker",
            sku="NK-TEST-001",
            category=self.category,
            description="Exquisite 22K BIS hallmarked gold choker",
            metal_type="GOLD",
            purity="22K",
            gross_weight=Decimal('35.500'),
            net_weight=Decimal('32.000'),
            stone_weight=Decimal('3.500'),
            making_charges=Decimal('8500.00'),
            base_price=Decimal('245000.00'),
            discount_percent=Decimal('5.00'),
            stock=5,
            availability='IN_STOCK',
            status='ACTIVE',
            is_new=True,
            is_trending=True,
            is_featured=True
        )

    def test_homepage_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AURA")
        self.assertContains(response, "22K Royal Temple Choker")

    def test_product_list_and_filter(self):
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

        # Test filter by metal
        response_filtered = self.client.get(reverse('product_list') + '?metal=GOLD')
        self.assertEqual(response_filtered.status_code, 200)
        self.assertContains(response_filtered, self.product.name)

    def test_product_detail_page(self):
        response = self.client.get(reverse('product_detail', kwargs={'slug': self.product.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.sku)
        self.assertContains(response, "BIS 916 Hallmark")
        # Final price calculation check
        self.assertEqual(self.product.final_price, Decimal('232750.00'))

    def test_cart_operations(self):
        # Add to cart
        response = self.client.post(reverse('cart_add'), {
            'product_id': self.product.id,
            'quantity': 2
        })
        self.assertEqual(response.status_code, 302)

        # View cart
        cart_resp = self.client.get(reverse('cart_detail'))
        self.assertEqual(cart_resp.status_code, 200)
        self.assertContains(cart_resp, self.product.name)

    def test_checkout_and_order_creation(self):
        self.client.login(username='cust_test', password='CustPass123')
        
        # Add to cart first
        self.client.post(reverse('cart_add'), {'product_id': self.product.id, 'quantity': 1})
        
        # Checkout POST
        checkout_data = {
            'full_name': 'Ananya Patel',
            'phone': '9876543210',
            'email': 'cust@test.com',
            'street_address': '123 Heritage Palace Road',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'pincode': '560001',
            'billing_same': '1',
            'payment_method': 'UPI',
        }
        response = self.client.post(reverse('checkout'), checkout_data)
        self.assertEqual(response.status_code, 302)

        # Order created in DB
        order = Order.objects.filter(customer_name='Ananya Patel').first()
        self.assertIsNotNone(order)
        self.assertTrue(order.order_number.startswith('GJ-'))
        self.assertEqual(order.items.count(), 1)

        # Check invoice view
        invoice_resp = self.client.get(reverse('order_invoice', kwargs={'order_number': order.order_number}))
        self.assertEqual(invoice_resp.status_code, 200)
        self.assertContains(invoice_resp, "TAX INVOICE")
        self.assertContains(invoice_resp, "HSN")

    def test_custom_jewellery_order_flow(self):
        self.client.login(username='cust_test', password='CustPass123')
        
        custom_data = {
            'full_name': 'Ananya Patel',
            'email': 'cust@test.com',
            'phone': '9876543210',
            'jewellery_type': 'RING',
            'metal_type': 'YELLOW_GOLD',
            'gold_purity': '22K',
            'expected_weight': '12.500',
            'preferred_budget': '90000',
            'ring_size': 'Indian 14',
            'design_description': 'Lotus flower motif ring with ruby petals and diamond centre.',
        }
        response = self.client.post(reverse('custom_order_create'), custom_data)
        self.assertEqual(response.status_code, 302)

        custom_order = CustomOrder.objects.filter(full_name='Ananya Patel').first()
        self.assertIsNotNone(custom_order)
        self.assertTrue(custom_order.request_id.startswith('CUST-'))

    def test_admin_dashboard_access(self):
        # Non-admin cannot access
        self.client.login(username='cust_test', password='CustPass123')
        resp = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(resp.status_code, 302)

        # Admin can access
        self.client.login(username='admin_test', password='AdminPass123')
        resp = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Executive Suite")
