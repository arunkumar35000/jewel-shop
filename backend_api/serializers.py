from rest_framework import serializers
from django.contrib.auth.models import User
from products.models import Product, ProductImage, Product360Image, Category, SubCategory
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem, Payment
from custom_orders.models import CustomOrder, CustomOrderImage, CustomOrderQuotation


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(source='products.count', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'is_active', 'product_count']


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
    count_360_frames = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'category', 'category_name', 'metal_type',
            'purity', 'gross_weight', 'net_weight', 'stone_weight', 'making_charges',
            'base_price', 'final_price', 'discount_percent', 'stock', 'availability',
            'status', 'is_featured', 'is_new', 'is_trending', 'is_bestseller',
            'has_360', 'count_360_frames', 'images', 'images_360'
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


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_name', 'product_sku', 'metal_type', 'purity',
            'gross_weight', 'unit_price', 'making_charges', 'quantity', 'total_price'
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    order_status_display = serializers.CharField(source='get_order_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'invoice_number', 'customer_name', 'customer_email',
            'customer_phone', 'shipping_address', 'billing_address', 'items_total',
            'making_charges_total', 'tax_amount', 'grand_total', 'payment_method',
            'payment_status', 'payment_status_display', 'order_status', 'order_status_display',
            'tracking_number', 'courier_partner', 'estimated_delivery', 'created_at', 'items'
        ]


class CustomOrderImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomOrderImage
        fields = ['id', 'image', 'caption', 'uploaded_at']


class CustomOrderQuotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomOrderQuotation
        fields = [
            'id', 'quotation_number', 'estimated_weight', 'metal_rate_applied',
            'making_charges', 'total_quoted_price', 'cad_design_file',
            'estimated_making_days', 'quotation_notes', 'status', 'created_at'
        ]


class CustomOrderSerializer(serializers.ModelSerializer):
    reference_images = CustomOrderImageSerializer(many=True, read_only=True)
    quotations = CustomOrderQuotationSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    jewellery_type_display = serializers.CharField(source='get_jewellery_type_display', read_only=True)
    metal_type_display = serializers.CharField(source='get_metal_type_display', read_only=True)

    class Meta:
        model = CustomOrder
        fields = [
            'id', 'request_id', 'full_name', 'email', 'phone', 'jewellery_type',
            'jewellery_type_display', 'metal_type', 'metal_type_display', 'gold_purity',
            'expected_weight', 'preferred_budget', 'design_description', 'status',
            'status_display', 'created_at', 'reference_images', 'quotations'
        ]


class CustomerDirectorySerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    orders_count = serializers.IntegerField(read_only=True)
    total_spent = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 'is_active', 'date_joined', 'orders_count', 'total_spent']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username
