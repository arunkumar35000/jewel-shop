from django import forms
from .models import CustomOrder, CustomOrderQuotation


class CustomOrderRequestForm(forms.ModelForm):
    class Meta:
        model = CustomOrder
        fields = [
            'full_name', 'email', 'phone', 'jewellery_type', 'metal_type', 'gold_purity',
            'expected_weight', 'preferred_budget', 'ring_size', 'necklace_length',
            'design_description', 'special_instructions', 'expected_delivery_date'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control py-2', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control py-2', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control py-2', 'placeholder': 'Mobile Number (+91)'}),
            'jewellery_type': forms.Select(attrs={'class': 'form-select py-2'}),
            'metal_type': forms.Select(attrs={'class': 'form-select py-2'}),
            'gold_purity': forms.Select(attrs={'class': 'form-select py-2'}),
            'expected_weight': forms.NumberInput(attrs={'class': 'form-control py-2', 'step': '0.1', 'placeholder': 'e.g. 20.000 grams'}),
            'preferred_budget': forms.NumberInput(attrs={'class': 'form-control py-2', 'step': '1000', 'placeholder': 'e.g. 150000'}),
            'ring_size': forms.TextInput(attrs={'class': 'form-control py-2', 'placeholder': 'e.g. Indian 14 / US 7 (optional)'}),
            'necklace_length': forms.TextInput(attrs={'class': 'form-control py-2', 'placeholder': 'e.g. 16 inches princess (optional)'}),
            'design_description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4,
                'placeholder': 'Describe your design vision in detail (e.g. motifs, stone arrangements, lock type, antique or glossy finish)...'
            }),
            'special_instructions': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'Special engravings, target delivery date preferences, packaging requirements...'
            }),
            'expected_delivery_date': forms.DateInput(attrs={'class': 'form-control py-2', 'type': 'date'}),
        }


class QuotationForm(forms.ModelForm):
    class Meta:
        model = CustomOrderQuotation
        fields = [
            'estimated_weight', 'metal_rate_applied', 'estimated_metal_cost',
            'making_charges', 'stone_charges', 'gst_amount', 'total_estimated_price',
            'estimated_making_days', 'design_notes', 'cad_design_file', 'valid_until'
        ]
        widgets = {
            'estimated_weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'metal_rate_applied': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estimated_metal_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'making_charges': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stone_charges': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'gst_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'total_estimated_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estimated_making_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'design_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cad_design_file': forms.FileInput(attrs={'class': 'form-control'}),
            'valid_until': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

