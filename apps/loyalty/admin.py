from django.contrib import admin
from django.utils.html import format_html
from .models import LoyaltyRule, LoyaltyAccount, LoyaltyTransaction


@admin.register(LoyaltyRule)
class LoyaltyRuleAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'rule_type', 'reward_type',
        'trigger_quantity', 'is_active',
        'valid_from', 'valid_until'
    ]
    list_filter = ['rule_type', 'reward_type', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['is_active']


@admin.register(LoyaltyAccount)
class LoyaltyAccountAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'get_level_badge', 'points',
        'lifetime_points', 'created_at'
    ]
    list_filter = ['level']
    search_fields = ['user__email', 'user__first_name']
    readonly_fields = ['created_at']

    def get_level_badge(self, obj):
        colors = {
            'bronze': '#cd7f32',
            'silver': '#9e9e9e',
            'gold': '#f39c12',
            'diamond': '#0288d1',
        }
        color = colors.get(obj.level, '#666')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;'
            'border-radius:12px;font-size:.8rem;">{}</span>',
            color, obj.level.capitalize()
        )
    get_level_badge.short_description = 'Nível'


@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'account', 'transaction_type', 'get_points_display',
        'description', 'created_at'
    ]
    list_filter = ['transaction_type', 'created_at']
    readonly_fields = ['created_at']

    def get_points_display(self, obj):
        color = 'success' if obj.points > 0 else 'danger'
        prefix = '+' if obj.points > 0 else ''
        return format_html(
            '<span class="badge bg-{}">{}{}</span>',
            color, prefix, obj.points
        )
    get_points_display.short_description = 'Pontos'