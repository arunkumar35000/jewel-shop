import math
from decimal import Decimal
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    icon_class = models.CharField(max_length=50, blank=True, default="bi-gem", help_text="Bootstrap or remix icon class")
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product_list_by_category', kwargs={'category_slug': self.slug})


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=150, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['category', 'name']
        unique_together = ('category', 'slug')
        verbose_name_plural = 'Subcategories'

    def __str__(self):
        return f"{self.category.name} > {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    METAL_TYPE_CHOICES = [
        ('GOLD', 'Gold'),
        ('DIAMOND', 'Diamond'),
        ('PLATINUM', 'Platinum'),
        ('SILVER', 'Silver'),
        ('ROSE_GOLD', 'Rose Gold'),
    ]

    PURITY_CHOICES = [
        ('24K', '24K (999 Pure)'),
        ('22K', '22K (916 Hallmark)'),
        ('18K', '18K (750 Gold)'),
        ('14K', '14K (585 Gold)'),
        ('950PT', '950 Platinum'),
        ('925SL', '925 Sterling Silver'),
    ]

    AVAILABILITY_CHOICES = [
        ('IN_STOCK', 'In Stock'),
        ('MADE_TO_ORDER', 'Made to Order'),
        ('OUT_OF_STOCK', 'Out of Stock'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active / Published'),
        ('DRAFT', 'Draft'),
        ('INACTIVE', 'Archived / Inactive'),
    ]

    GENDER_CHOICES = [
        ('WOMEN', 'Women'),
        ('MEN', 'Men'),
        ('UNISEX', 'Unisex'),
        ('KIDS', 'Kids'),
    ]

    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    sku = models.CharField(max_length=50, unique=True, help_text="Unique Product Code / SKU")
    
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    
    description = models.TextField(help_text="Detailed luxury jewellery description")
    specifications = models.TextField(blank=True, help_text="Design dimensions, polish, lock type, certificate details")
    
    metal_type = models.CharField(max_length=20, choices=METAL_TYPE_CHOICES, default='GOLD')
    purity = models.CharField(max_length=20, choices=PURITY_CHOICES, default='22K')
    
    gross_weight = models.DecimalField(
        max_digits=8, decimal_places=3,
        help_text="Gross Weight in grams (e.g. 15.420)",
        validators=[MinValueValidator(Decimal('0.001'))]
    )
    net_weight = models.DecimalField(
        max_digits=8, decimal_places=3,
        help_text="Net Gold Weight in grams excluding stones",
        validators=[MinValueValidator(Decimal('0.001'))]
    )
    stone_weight = models.DecimalField(
        max_digits=8, decimal_places=3, default=Decimal('0.000'),
        help_text="Weight of embedded gemstones/diamonds in carats/grams"
    )
    
    making_charges = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'),
        help_text="Making / Craftsmanship charges in INR"
    )
    
    base_price = models.DecimalField(
        max_digits=12, decimal_places=2,
        help_text="Original Retail Selling Price in INR",
        validators=[MinValueValidator(Decimal('1.00'))]
    )
    discount_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('0.00'),
        help_text="Discount percentage (e.g. 10.00 for 10% off)"
    )
    
    stock = models.PositiveIntegerField(default=1, help_text="Available inventory units")
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='IN_STOCK')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    gender = models.CharField(max_length=15, choices=GENDER_CHOICES, default='WOMEN')
    hallmark_certified = models.BooleanField(default=True, help_text="BIS 916 Hallmark / IGI / SGL Certified")
    certificate_number = models.CharField(max_length=100, blank=True, default="BIS-916-IND")
    
    # Diamond Specific Attributes
    diamond_clarity = models.CharField(max_length=50, blank=True, default="VVS-VS")
    diamond_color = models.CharField(max_length=50, blank=True, default="E-F Colorless")
    diamond_cut = models.CharField(max_length=50, blank=True, default="Excellent Ideal Cut")
    
    # Flags
    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.sku}) - ₹{self.final_price}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def final_price(self):
        """Calculates final price after applying discount percentage."""
        if self.discount_percent and self.discount_percent > Decimal('0'):
            discount = (self.base_price * self.discount_percent) / Decimal('100.0')
            return round(self.base_price - discount, 2)
        return round(self.base_price, 2)

    @property
    def discount_amount(self):
        if self.discount_percent and self.discount_percent > Decimal('0'):
            return round((self.base_price * self.discount_percent) / Decimal('100.0'), 2)
        return Decimal('0.00')

    @property
    def primary_image(self):
        """Returns the primary image, or first image, or None."""
        first_img = self.images.filter(is_primary=True).first()
        if not first_img:
            first_img = self.images.first()
        return first_img

    @property
    def secondary_image(self):
        """Returns the second image for hover flip effect."""
        imgs = list(self.images.all()[:2])
        if len(imgs) > 1:
            return imgs[1]
        return None

    @property
    def has_360(self):
        return self.images_360.exists()

    @property
    def count_360_frames(self):
        return self.images_360.count()

    @property
    def average_rating(self):
        approved_reviews = self.reviews.filter(is_approved=True)
        if approved_reviews.exists():
            avg = approved_reviews.aggregate(models.Avg('rating'))['rating__avg']
            return round(avg, 1)
        return 5.0

    @property
    def review_count(self):
        return self.reviews.filter(is_approved=True).count()

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    is_primary = models.BooleanField(default=False)
    alt_text = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['-is_primary', 'sort_order', 'id']

    def __str__(self):
        return f"Image for {self.product.name} ({'Primary' if self.is_primary else 'Gallery'})"

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class Product360Image(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images_360')
    image = models.ImageField(upload_to='products/360/')
    frame_number = models.PositiveIntegerField(help_text="Sequence frame index (1 to N)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['frame_number']
        unique_together = ('product', 'frame_number')

    def __str__(self):
        return f"{self.product.name} - Frame {self.frame_number}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_reviews')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating between 1 and 5"
    )
    title = models.CharField(max_length=150)
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.rating}★ on {self.product.name}"
