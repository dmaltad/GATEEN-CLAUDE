from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Product, Category, Brand


class ProductListView(ListView):
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        qs = Product.objects.filter(
            is_active=True,
        ).exclude(
            # Exclui produtos sem estoque (stock não existe OU quantity <= 0)
            Q(stock__isnull=True) | Q(stock__quantity__lte=0)
        ).select_related('category', 'brand', 'stock')

        # Filtros opcionais
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))

        category_slug = self.kwargs.get('category_slug') or self.request.GET.get('category')
        if category_slug:
            qs = qs.filter(category__slug=category_slug)

        species = self.request.GET.get('species')
        if species:
            qs = qs.filter(species=species)

        order = self.request.GET.get('order', '-created_at')
        allowed_orders = ['price', '-price', 'name', '-name', '-created_at']
        if order in allowed_orders:
            qs = qs.order_by(order)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.filter(is_active=True)
        ctx['query'] = self.request.GET.get('q', '')
        ctx['species_choices'] = Product.SPECIES_CHOICES
        ctx['cat'] = self.kwargs.get('category_slug') or self.request.GET.get('category', '')
        ctx['order_options'] = [
            {'val': '-created_at', 'label': 'Mais recentes',  'icon': 'fa-clock'},
            {'val': 'price',       'label': 'Menor preço',    'icon': 'fa-arrow-up'},
            {'val': '-price',      'label': 'Maior preço',    'icon': 'fa-arrow-down'},
            {'val': 'name',        'label': 'A-Z',            'icon': 'fa-sort-alpha-down'},
        ]
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