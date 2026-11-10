from django import forms
from .models import Product, ProductImage, Product360Image, Category, SubCategory, Review


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'category', 'subcategory', 'description', 'specifications',
            'metal_type', 'purity', 'gross_weight', 'net_weight', 'stone_weight',
            'making_charges', 'base_price', 'discount_percent', 'stock', 'availability',
            'status', 'gender', 'hallmark_certified', 'certificate_number',
            'is_featured', 'is_trending', 'is_new', 'is_bestseller'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'subcategory': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'specifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'metal_type': forms.Select(attrs={'class': 'form-select'}),
            'purity': forms.Select(attrs={'class': 'form-select'}),
            'gross_weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'net_weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'stone_weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'making_charges': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'base_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'discount_percent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'availability': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'certificate_number': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'is_primary', 'alt_text', 'sort_order']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'alt_text': forms.TextInput(attrs={'class': 'form-control'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'icon_class', 'is_featured', 'is_active', 'display_order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'icon_class': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. bi-gem'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(5, '5 Stars - Exceptional'), (4, '4 Stars - Very Good'), (3, '3 Stars - Good'), (2, '2 Stars - Fair'), (1, '1 Star - Poor')], attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Headline for your review'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe craftsmanship, hallmark authenticity, shine, and fit...'}),
        }

