from django.contrib import admin
from django.utils.html import format_html
from .models import Event, Promotion


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_thumb', 'title', 'event_type',
        'start_date', 'is_active', 'is_featured'
    ]
    list_filter = ['event_type', 'is_active', 'is_featured']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_active', 'is_featured']

    fieldsets = (
        ('Identificação', {
            'fields': ('title', 'slug', 'event_type')
        }),
        ('Conteúdo', {
            'fields': ('description', 'short_description', 'image', 'banner')
        }),
        ('Data e Local', {
            'fields': ('start_date', 'end_date', 'location', 'is_online', 'online_link')
        }),
        ('Visibilidade', {
            'fields': ('is_active', 'is_featured')
        }),
    )

    def get_image_thumb(self, obj):
        src = obj.banner.url if obj.banner else (obj.image.url if obj.image else None)
        if src:
            return format_html(
                '<img src="{}" style="width:60px;height:40px;'
                'object-fit:cover;border-radius:4px;">', src
            )
        return '—'
    get_image_thumb.short_description = ''


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'discount_type', 'get_discount_display',
        'coupon_code', 'start_date', 'end_date', 'is_active', 'used_count'
    ]
    list_filter = ['discount_type', 'is_active']
    search_fields = ['title', 'coupon_code']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_active']
    filter_horizontal = ['applicable_products', 'applicable_categories']

    def get_discount_display(self, obj):
        if obj.discount_type == 'percentage':
            return format_html(
                '<span class="badge bg-success">-{}%</span>',
                obj.discount_value
            )
        elif obj.discount_type == 'fixed':
            return format_html(
                '<span class="badge bg-primary">-R$ {}</span>',
                obj.discount_value
            )
        return format_html('<span class="badge bg-info">Frete grátis</span>')
    get_discount_display.short_description = 'Desconto'