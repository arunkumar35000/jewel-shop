from django.test import TestCase, Client
from django.urls import reverse
from products.models import Product, Category, Product360Image
from decimal import Decimal


class APITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Rings", slug="rings")
        self.product = Product.objects.create(
            name="Solitaire Diamond Ring",
            sku="RG-API-001",
            category=self.category,
            metal_type="DIAMOND",
            purity="18K",
            gross_weight=Decimal('5.500'),
            net_weight=Decimal('5.200'),
            stone_weight=Decimal('1.000'),
            base_price=Decimal('120000.00'),
            stock=4,
            status='ACTIVE'
        )

    def test_product_list_api(self):
        response = self.client.get(reverse('api_product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data['results']) >= 1)
        self.assertEqual(response.data['results'][0]['sku'], 'RG-API-001')

    def test_product_detail_api(self):
        response = self.client.get(reverse('api_product_detail', kwargs={'slug': self.product.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Solitaire Diamond Ring')

    def test_360_frames_api(self):
        response = self.client.get(reverse('api_product_360_frames', kwargs={'slug': self.product.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_frames', response.data)
