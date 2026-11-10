from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from products.models import Product


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        owner = self.user.username if self.user else f"Session {self.session_key[:8]}"
        return f"Cart #{self.id} ({owner})"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        """Total product price after discounts."""
        return sum(item.item_subtotal for item in self.items.all())

    @property
    def total_making_charges(self):
        return sum(item.item_making_charges for item in self.items.all())

    @property
    def total_gross_weight(self):
        return sum(item.product.gross_weight * item.quantity for item in self.items.all())

    @property
    def gst_amount(self):
        """Jewellery GST (3% on subtotal)."""
        gst_percent = getattr(settings, 'JEWELLERY_GST_PERCENT', Decimal('3.00'))
        return round((self.subtotal * Decimal(str(gst_percent))) / Decimal('100.00'), 2)

    @property
    def grand_total(self):
        return round(self.subtotal + self.gst_amount, 2)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cart', 'product')
        ordering = ['id']

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def item_subtotal(self):
        return round(self.product.final_price * self.quantity, 2)

    @property
    def item_making_charges(self):
        return round(self.product.making_charges * self.quantity, 2)
