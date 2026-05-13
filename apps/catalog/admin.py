from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Brand, Product, ProductImage, Stock, StockMovement


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 2
    fields = ['image', 'alt', 'order']


class StockInline(admin.StackedInline):
    model = Stock
    extra = 0
    fields = ['quantity', 'min_quantity', 'reserved_quantity']
    can_delete = False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'get_logo']
    list_editable = ['is_active']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

    def get_logo(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="height:30px;border-radius:4px;">',
                obj.logo.url
            )
        return '—'
    get_logo.short_description = 'Logo'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_thumb', 'name', 'category', 'brand',
        'price', 'promotional_price', 'get_stock_qty',
        'is_active', 'is_featured'
    ]
    list_filter = ['category', 'brand', 'species', 'is_active', 'is_featured']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'is_featured', 'promotional_price']
    inlines = [ProductImageInline, StockInline]
    list_per_page = 25

    fieldsets = (
        ('Identificação', {
            'fields': ('name', 'slug', 'category', 'brand', 'species')
        }),
        ('Preço', {
            'fields': ('price', 'promotional_price')
        }),
        ('Conteúdo', {
            'fields': ('description', 'short_description', 'image', 'weight')
        }),
        ('Visibilidade', {
            'fields': ('is_active', 'is_featured')
        }),
    )

    def get_image_thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:40px;height:40px;'
                'object-fit:cover;border-radius:6px;">',
                obj.image.url
            )
        return format_html(
            '<div style="width:40px;height:40px;background:#f0f0f0;'
            'border-radius:6px;display:flex;align-items:center;'
            'justify-content:center;"><i class="fas fa-image" '
            'style="color:#ccc;"></i></div>'
        )
    get_image_thumb.short_description = ''

    def get_stock_qty(self, obj):
        try:
            qty = obj.stock.quantity
            color = 'danger' if qty == 0 else 'warning' if qty <= 5 else 'success'
            return format_html(
                '<span class="badge bg-{}">{} un.</span>', color, qty
            )
        except Exception:
            return format_html('<span class="badge bg-secondary">—</span>')
    get_stock_qty.short_description = 'Estoque'


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'get_qty_display', 'min_quantity',
        'reserved_quantity', 'get_status'
    ]
    list_filter = []
    search_fields = ['product__name']
    readonly_fields = ['product']

    def get_qty_display(self, obj):
        return format_html('<strong>{}</strong>', obj.quantity)
    get_qty_display.short_description = 'Quantidade'

    def get_status(self, obj):
        if obj.is_out:
            return format_html('<span class="badge bg-danger">Sem estoque</span>')
        elif obj.is_low:
            return format_html('<span class="badge bg-warning text-dark">Estoque baixo</span>')
        return format_html('<span class="badge bg-success">Normal</span>')
    get_status.short_description = 'Status'


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'movement_type', 'quantity',
        'current_stock', 'created_by', 'created_at'
    ]
    list_filter = ['movement_type', 'created_at']
    readonly_fields = ['created_at', 'created_by', 'current_stock']
    search_fields = ['product__name', 'reason']

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)