from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Product, Category, Brand


class ProductListView(ListView):
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related('category', 'brand')
        category_slug = self.kwargs.get('category_slug')
        brand_slug = self.kwargs.get('brand_slug')
        q = self.request.GET.get('q')
        species = self.request.GET.get('species')
        order = self.request.GET.get('order', '-created_at')

        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        if brand_slug:
            qs = qs.filter(brand__slug=brand_slug)
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
        if species and species != 'all':
            qs = qs.filter(species__in=[species, 'all'])

        valid_orders = ['-created_at', 'price', '-price', 'name']
        if order in valid_orders:
            qs = qs.order_by(order)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.filter(is_active=True)
        ctx['brands'] = Brand.objects.filter(is_active=True)
        ctx['selected_category'] = self.kwargs.get('category_slug')
        ctx['query'] = self.request.GET.get('q', '')
        return ctx


class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category', 'brand').prefetch_related('images', 'stock')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.filter(is_active=True)
        ctx['brands'] = Brand.objects.filter(is_active=True)
        ctx['selected_category'] = self.kwargs.get('category_slug')
        ctx['query'] = self.request.GET.get('q', '')
        ctx['species_choices'] = [
            ('all', 'Todos'),
            ('dog', 'Cães'),
            ('cat', 'Gatos'),
            ('bird', 'Pássaros'),
            ('fish', 'Peixes'),
        ]
        return ctx