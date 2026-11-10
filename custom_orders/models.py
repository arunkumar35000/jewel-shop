import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class CustomOrder(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('UNDER_REVIEW', 'Under Review'),
        ('DESIGN_PREPARATION', 'Design Preparation & 3D CAD'),
        ('QUOTATION_SENT', 'Quotation Sent'),
        ('APPROVED', 'Quotation Approved'),
        ('IN_PRODUCTION', 'In Production / Handcrafting'),
        ('READY_FOR_DELIVERY', 'Ready for Delivery & Hallmarking'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    JEWELLERY_TYPE_CHOICES = [
        ('RING', 'Custom Ring / Solitaire Engagement'),
        ('NECKLACE', 'Royal Necklace / Choker'),
        ('PENDANT', 'Designer Pendant'),
        ('EARRINGS', 'Jhumkas / Danglers / Studs'),
        ('BANGLES', 'Bangles / Kada / Bracelet'),
        ('BRIDAL_SET', 'Complete Bridal Trousseau Set'),
        ('MANGALSUTRA', 'Contemporary Mangalsutra'),
        ('CHAIN', 'Gold Chain / Rope Chain'),
        ('OTHER', 'Other Custom Design'),
    ]

    METAL_CHOICES = [
        ('YELLOW_GOLD', 'Yellow Gold'),
        ('ROSE_GOLD', 'Rose Gold'),
        ('WHITE_GOLD', 'White Gold'),
        ('PLATINUM', 'Platinum (950)'),
        ('SILVER', 'Sterling Silver (925)'),
    ]

    PURITY_CHOICES = [
        ('24K', '24K (999 Pure)'),
        ('22K', '22K (916 BIS Hallmark)'),
        ('18K', '18K (750 Hallmark)'),
        ('14K', '14K (585 Hallmark)'),
        ('950PT', '950 Platinum'),
    ]

    request_id = models.CharField(max_length=50, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='custom_orders')
    
    # Customer Details
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Jewellery Preferences
    jewellery_type = models.CharField(max_length=30, choices=JEWELLERY_TYPE_CHOICES)
    metal_type = models.CharField(max_length=30, choices=METAL_CHOICES, default='YELLOW_GOLD')
    gold_purity = models.CharField(max_length=20, choices=PURITY_CHOICES, default='22K')
    expected_weight = models.DecimalField(
        max_digits=8, decimal_places=3,
        help_text="Target weight in grams (e.g. 25.500)"
    )
    preferred_budget = models.DecimalField(
        max_digits=12, decimal_places=2,
        help_text="Customer target budget in INR"
    )
    
    # Sizing
    ring_size = models.CharField(max_length=50, blank=True, help_text="e.g. US 7 / Indian 14")
    necklace_length = models.CharField(max_length=50, blank=True, help_text="e.g. 16 inches / 18 inches princess")
    
    # Design Specifications
    design_description = models.TextField(help_text="Detailed description of the envisioned design")
    special_instructions = models.TextField(blank=True, help_text="Engravings, gemstone choices, polish preferences")
    expected_delivery_date = models.DateField(null=True, blank=True)
    
    # Workflow
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING')
    admin_notes = models.TextField(blank=True, help_text="Internal workshop & artisan notes")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Custom Request #{self.request_id} - {self.full_name} ({self.get_jewellery_type_display()})"

    def save(self, *args, **kwargs):
        if not self.request_id:
            stamp = timezone.now().strftime("%Y%m%d")
            rand_suffix = uuid.uuid4().hex[:5].upper()
            self.request_id = f"CUST-{stamp}-{rand_suffix}"
        super().save(*args, **kwargs)

    @property
    def latest_quotation(self):
        return self.quotations.last()

    @property
    def status_step_index(self):
        steps = [
            'PENDING', 'UNDER_REVIEW', 'DESIGN_PREPARATION',
            'QUOTATION_SENT', 'APPROVED', 'IN_PRODUCTION',
            'READY_FOR_DELIVERY', 'DELIVERED'
        ]
        if self.status in steps:
            return steps.index(self.status) + 1
        return 0


class CustomOrderImage(models.Model):
    custom_order = models.ForeignKey(CustomOrder, on_delete=models.CASCADE, related_name='reference_images')
    image = models.ImageField(upload_to='custom_orders/references/')
    caption = models.CharField(max_length=150, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reference image for {self.custom_order.request_id}"


class CustomOrderQuotation(models.Model):
    STATUS_CHOICES = [
        ('SENT', 'Quotation Sent to Customer'),
        ('ACCEPTED', 'Accepted by Customer'),
        ('REVISION_REQUESTED', 'Revision Requested'),
        ('REJECTED', 'Rejected'),
    ]

    custom_order = models.ForeignKey(CustomOrder, on_delete=models.CASCADE, related_name='quotations')
    quotation_number = models.CharField(max_length=50, unique=True, editable=False)
    
    estimated_weight = models.DecimalField(max_digits=8, decimal_places=3, help_text="Weight in grams")
    metal_rate_applied = models.DecimalField(max_digits=10, decimal_places=2, help_text="Rate per gram")
    estimated_metal_cost = models.DecimalField(max_digits=12, decimal_places=2)
    making_charges = models.DecimalField(max_digits=10, decimal_places=2)
    stone_charges = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_estimated_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    estimated_making_days = models.PositiveIntegerField(default=15)
    design_notes = models.TextField(blank=True, help_text="Artisan breakdown & hallmark notes")
    cad_design_file = models.FileField(upload_to='custom_orders/cad/', blank=True, null=True)
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='SENT')
    customer_feedback = models.TextField(blank=True)
    valid_until = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Quote #{self.quotation_number} for {self.custom_order.request_id} - ₹{self.total_estimated_price}"

    def save(self, *args, **kwargs):
        if not self.quotation_number:
            stamp = timezone.now().strftime("%Y%m%d")
            rand = uuid.uuid4().hex[:4].upper()
            self.quotation_number = f"QTE-{stamp}-{rand}"
        super().save(*args, **kwargs)
