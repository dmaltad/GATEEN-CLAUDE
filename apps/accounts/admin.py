from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Address, Pet


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    fields = ['label', 'street', 'number', 'city', 'state', 'is_default']


class PetInline(admin.TabularInline):
    model = Pet
    extra = 0
    fields = ['name', 'species', 'breed', 'size']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'email', 'get_full_name_display', 'phone',
        'is_active', 'is_staff', 'date_joined', 'get_groups'
    ]
    list_filter = ['is_active', 'is_staff', 'groups']
    search_fields = ['email', 'first_name', 'last_name', 'cpf']
    ordering = ['-date_joined']
    inlines = [AddressInline, PetInline]

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações pessoais', {
            'fields': ('first_name', 'last_name', 'cpf', 'phone', 'birth_date', 'avatar')
        }),
        ('Permissões', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        ('Datas', {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',),
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    readonly_fields = ['date_joined', 'last_login']
    filter_horizontal = ('groups', 'user_permissions',)

    def get_full_name_display(self, obj):
        return obj.get_full_name()
    get_full_name_display.short_description = 'Nome completo'

    def get_groups(self, obj):
        groups = obj.groups.values_list('name', flat=True)
        if not groups:
            return format_html('<span class="text-muted">—</span>')
        badges = ''.join(
            f'<span class="badge bg-primary me-1">{g}</span>'
            for g in groups
        )
        return format_html(badges)
    get_groups.short_description = 'Grupos'
    get_groups.allow_tags = True


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'species', 'breed', 'size']
    list_filter = ['species', 'size']
    search_fields = ['name', 'owner__email', 'owner__first_name']