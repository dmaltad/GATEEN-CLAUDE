from django.contrib import admin
from django.utils.html import format_html
from .models import ServicePlan, PlanFeature, UserPlan


class PlanFeatureInline(admin.TabularInline):
    model = PlanFeature
    extra = 3
    fields = ['description', 'is_included']


@admin.register(ServicePlan)
class ServicePlanAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'get_price_display', 'period',
        'food_bags_per_month', 'grooming_sessions_per_month',
        'includes_health_plan', 'is_active', 'is_featured'
    ]
    list_editable = ['is_active', 'is_featured']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [PlanFeatureInline]

    def get_price_display(self, obj):
        return format_html(
            '<strong style="color:{};">R$ {}</strong>',
            obj.color, obj.price
        )
    get_price_display.short_description = 'Preço'


@admin.register(UserPlan)
class UserPlanAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'plan', 'pet', 'status',
        'start_date', 'end_date',
        'food_bags_used', 'grooming_sessions_used'
    ]
    list_filter = ['status', 'plan']
    search_fields = ['user__email', 'user__first_name']
    readonly_fields = ['created_at']