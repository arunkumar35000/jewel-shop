from rest_framework import serializers
from products.models import Product, ProductImage, Product360Image, Category
from cart.models import Cart, CartItem
from custom_orders.models import CustomOrder


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_primary', 'alt_text', 'sort_order']


class Product360ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product360Image
        fields = ['id', 'image', 'frame_number']


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    images_360 = Product360ImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    final_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'category', 'category_name', 'metal_type',
            'purity', 'gross_weight', 'net_weight', 'stone_weight', 'making_charges',
            'base_price', 'final_price', 'discount_percent', 'stock', 'availability',
            'status', 'images', 'images_360'
        ]


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    item_subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'item_subtotal']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    gst_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    grand_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'total_items', 'subtotal', 'gst_amount', 'grand_total', 'items']


class CustomOrderSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = CustomOrder
        fields = [
            'request_id', 'full_name', 'email', 'phone', 'jewellery_type',
            'metal_type', 'gold_purity', 'expected_weight', 'preferred_budget',
            'design_description', 'status', 'status_display', 'created_at'
        ]

