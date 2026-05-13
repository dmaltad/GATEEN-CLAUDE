from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, CashRegister, CashTransaction


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    # Usar o método get_subtotal_display em vez da property subtotal
    readonly_fields = ['get_subtotal_display']
    fields = ['product', 'quantity', 'unit_price', 'get_subtotal_display']

    def get_subtotal_display(self, obj):
        if obj.unit_price is None or obj.quantity is None:
            return '—'
        return format_html('<strong>R$ {:.2f}</strong>', obj.unit_price * obj.quantity)
    get_subtotal_display.short_description = 'Subtotal'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'user', 'status', 'total',
        'delivery_type', 'payment_method', 'created_at'
    ]
    list_filter = ['status', 'delivery_type', 'payment_method', 'created_at']
    search_fields = ['order_number', 'user__email', 'user__first_name']
    inlines = [OrderItemInline]
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(CashRegister)
class CashRegisterAdmin(admin.ModelAdmin):
    list_display = ['opened_at', 'opened_by', 'status', 'opening_balance', 'closing_balance']
    list_filter = ['status']


@admin.register(CashTransaction)
class CashTransactionAdmin(admin.ModelAdmin):
    list_display = ['cash_register', 'transaction_type', 'amount', 'payment_method', 'created_at']
    list_filter = ['transaction_type', 'payment_method']