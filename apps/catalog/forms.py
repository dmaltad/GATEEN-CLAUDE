from django import forms
from django.utils.text import slugify
from .models import Product, Category, Brand


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'brand', 'species',
            'price', 'promotional_price',
            'description', 'short_description',
            'image', 'weight',
            'is_active', 'is_featured',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do produto',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4,
            }),
            'short_description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01',
            }),
            'promotional_price': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01',
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.001',
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'brand':    forms.Select(attrs={'class': 'form-select'}),
            'species':  forms.Select(attrs={'class': 'form-select'}),
            'is_active':   forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save(self, commit=True):
        product = super().save(commit=False)
        if not product.slug:
            product.slug = slugify(product.name)
        # Garante slug único
        from .models import Product as P
        base, n = product.slug, 1
        while P.objects.filter(slug=product.slug).exclude(pk=product.pk).exists():
            product.slug = f'{base}-{n}'
            n += 1
        if commit:
            product.save()
        return product