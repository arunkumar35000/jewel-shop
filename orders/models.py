import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from products.models import Product


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('PENDING', 'Pending Confirmation'),
        ('CONFIRMED', 'Order Confirmed'),
        ('CRAFTING', 'Hallmarking & Crafting'),
        ('SHIPPED', 'Dispatched / In Transit'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('COD', 'Cash on Delivery (Insured)'),
        ('UPI', 'UPI / QR Code (Instant)'),
        ('ONLINE_CARD', 'Credit / Debit Card / NetBanking'),
        ('BANK_TRANSFER', 'Direct Bank Transfer / NEFT'),
        ('STRIPE', 'Stripe Online Payment (Cards & Global)'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending Payment'),
        ('PAID', 'Payment Received'),
        ('FAILED', 'Payment Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    order_number = models.CharField(max_length=50, unique=True, editable=False)
    invoice_number = models.CharField(max_length=60, unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    
    # Customer Details Snapshot
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    
    # Address Snapshots
    shipping_address = models.TextField(help_text="Full shipping destination address snapshot")
    billing_address = models.TextField(help_text="Full billing address snapshot")
    
    # Financial Breakdown
    items_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    making_charges_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="GST 3%")
    shipping_charges = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'), help_text="Insured delivery")
    grand_total = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Status & Payment
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='UPI')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    order_status = models.CharField(max_length=25, choices=ORDER_STATUS_CHOICES, default='PENDING')
    
    # Tracking
    tracking_number = models.CharField(max_length=100, blank=True, default="")
    courier_partner = models.CharField(max_length=100, blank=True, default="BlueDart Apex Gold Insured")
    estimated_delivery = models.DateField(null=True, blank=True)
    order_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_number} ({self.customer_name}) - ₹{self.grand_total}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            stamp = timezone.now().strftime("%Y%m%d")
            rand_suffix = uuid.uuid4().hex[:6].upper()
            self.order_number = f"GJ-{stamp}-{rand_suffix}"
        if not self.invoice_number:
            self.invoice_number = f"INV-{self.order_number}"
        super().save(*args, **kwargs)

    @property
    def can_cancel(self):
        return self.order_status in ['PENDING', 'CONFIRMED']

    @property
    def progress_percentage(self):
        mapping = {
            'PENDING': 15,
            'CONFIRMED': 35,
            'CRAFTING': 55,
            'SHIPPED': 75,
            'OUT_FOR_DELIVERY': 90,
            'DELIVERED': 100,
            'CANCELLED': 0,
        }
        return mapping.get(self.order_status, 10)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')
    
    # Snapshot of product details at time of purchase
    product_name = models.CharField(max_length=250)
    product_sku = models.CharField(max_length=50)
    metal_type = models.CharField(max_length=30)
    purity = models.CharField(max_length=30)
    gross_weight = models.DecimalField(max_digits=8, decimal_places=3)
    net_weight = models.DecimalField(max_digits=8, decimal_places=3)
    stone_weight = models.DecimalField(max_digits=8, decimal_places=3, default=Decimal('0.000'))
    
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    making_charges = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product_name} (Order #{self.order.order_number})"


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('SUCCESS', 'Success'),
        ('PENDING', 'Pending'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    transaction_id = models.CharField(max_length=120, unique=True)
    payment_method = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='SUCCESS')
    payment_details = models.TextField(blank=True, help_text="Transaction reference details, gateway payloads")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.transaction_id} for Order #{self.order.order_number} ({self.status})"
