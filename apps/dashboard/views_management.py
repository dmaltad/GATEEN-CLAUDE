"""
Views de gestão personalizadas por cargo.
Substituem o Django Admin para o fluxo de funcionários.
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import timedelta


def group_required(*group_names):
    """Decorator: exige que o usuário pertença a um dos grupos OU seja superuser."""
    def decorator(view_func):
        @login_required
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_staff:
                messages.error(request, 'Acesso restrito.')
                return redirect('home')
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            if request.user.groups.filter(name__in=group_names).exists():
                return view_func(request, *args, **kwargs)
            messages.error(request, 'Seu cargo não permite acessar esta área.')
            return redirect('dashboard:home')
        return _wrapped
    return decorator


# ══════════════════════════════════════════════════════
# DASHBOARD HOME
# ══════════════════════════════════════════════════════

@login_required
def dashboard_home(request):
    from apps.orders.models import Order
    from apps.catalog.models import Stock
    from apps.accounts.models import User
    from apps.events.models import Event

    if not request.user.is_staff:
        messages.error(request, 'Acesso restrito a funcionários.')
        return redirect('home')

    today     = timezone.now().date()
    month_ago = today - timedelta(days=30)
    week_ago  = today - timedelta(days=7)

    paid_statuses = ['confirmed', 'preparing', 'ready', 'shipped', 'delivered']

    total_orders_today = Order.objects.filter(created_at__date=today).count()
    revenue_today = (
        Order.objects.filter(created_at__date=today, status__in=paid_statuses)
        .aggregate(total=Sum('total'))['total'] or 0
    )
    revenue_month = (
        Order.objects.filter(created_at__date__gte=month_ago, status__in=paid_statuses)
        .aggregate(total=Sum('total'))['total'] or 0
    )
    new_users = User.objects.filter(date_joined__date__gte=week_ago).count()

    low_stock = (
        Stock.objects.filter(quantity__lte=5)
        .select_related('product')[:10]
    )
    recent_orders = (
        Order.objects.select_related('user')
        .order_by('-created_at')[:10]
    )

    # Eventos ativos (em andamento ou futuros)
    now = timezone.now()
    active_events = Event.objects.filter(
        is_active=True,
        start_date__gte=now - timedelta(days=1),
    ).order_by('start_date')[:5]

    shortcuts = [
        {'label': 'Produtos',      'icon': 'fa-box',           'color': '#8A4B9F', 'url': '/dashboard/gestao/produtos/'},
        {'label': 'Pedidos',       'icon': 'fa-shopping-cart', 'color': '#E74C3C', 'url': '/dashboard/gestao/pedidos/'},
        {'label': 'Eventos',       'icon': 'fa-calendar',      'color': '#F4B942', 'url': '/dashboard/gestao/eventos/'},
        {'label': 'Planos',        'icon': 'fa-star',          'color': '#FF9800', 'url': '/dashboard/gestao/planos/'},
        {'label': 'Fidelidade',    'icon': 'fa-gift',          'color': '#9C27B0', 'url': '/dashboard/gestao/fidelidade/'},
        {'label': 'Usuários',      'icon': 'fa-users',         'color': '#2196F3', 'url': '/dashboard/gestao/usuarios/'},
        {'label': 'Cargos',        'icon': 'fa-user-tag',      'color': '#607D8B', 'url': '/dashboard/gestao/cargos/'},
        {'label': 'Planos ativos', 'icon': 'fa-id-card',       'color': '#009688', 'url': '/dashboard/gestao/planos/ativos/'},
        {'label': 'Categorias',    'icon': 'fa-th',            'color': '#795548', 'url': '/dashboard/gestao/categorias/'},
    ]

    return render(request, 'dashboard/home.html', {
        'total_orders_today': total_orders_today,
        'revenue_today':      revenue_today,
        'revenue_month':      revenue_month,
        'low_stock':          low_stock,
        'recent_orders':      recent_orders,
        'new_users':          new_users,
        'shortcuts':          shortcuts,
        'active_events':      active_events,
    })


# ══════════════════════════════════════════════════════
# PRODUTOS
# ══════════════════════════════════════════════════════

@group_required('Gerente', 'Estoquista')
def product_list(request):
    from apps.catalog.models import Product, Category
    qs = Product.objects.select_related('category', 'brand', 'stock').all()

    q = request.GET.get('q', '')
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(brand__name__icontains=q))

    cat = request.GET.get('category', '')
    if cat:
        qs = qs.filter(category__slug=cat)

    stock_filter = request.GET.get('stock', '')
    if stock_filter == 'low':
        qs = qs.filter(stock__quantity__lte=5, stock__quantity__gt=0)
    elif stock_filter == 'out':
        qs = qs.filter(Q(stock__isnull=True) | Q(stock__quantity__lte=0))

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'dashboard/management/product_list.html', {
        'page_obj':    page_obj,
        'categories':  Category.objects.filter(is_active=True),
        'q':           q,
        'cat':         cat,
        'stock_filter': stock_filter,
    })


@group_required('Gerente', 'Estoquista')
def product_create(request):
    from apps.catalog.forms import ProductForm
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Produto "{product.name}" criado!')
            return redirect('dashboard:product_list')
    else:
        form = ProductForm()
    return render(request, 'dashboard/management/product_form.html', {
        'form': form, 'action': 'Criar produto'
    })


@group_required('Gerente', 'Estoquista')
def product_edit(request, pk):
    from apps.catalog.models import Product
    from apps.catalog.forms import ProductForm
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{product.name}" atualizado!')
            return redirect('dashboard:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'dashboard/management/product_form.html', {
        'form': form, 'product': product, 'action': 'Editar produto'
    })


@group_required('Gerente')
def product_delete(request, pk):
    from apps.catalog.models import Product
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'"{name}" removido.')
        return redirect('dashboard:product_list')
    return render(request, 'dashboard/management/confirm_delete.html', {
        'object': product, 'type': 'produto'
    })


# ══════════════════════════════════════════════════════
# CATEGORIAS
# ══════════════════════════════════════════════════════

@group_required('Gerente', 'Estoquista')
def category_list(request):
    from apps.catalog.models import Category
    qs = Category.objects.all().order_by('order', 'name')
    q = request.GET.get('q', '')
    if q:
        qs = qs.filter(name__icontains=q)
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/management/category_list.html', {
        'page_obj': page_obj, 'q': q,
    })


@group_required('Gerente', 'Estoquista')
def category_create(request):
    from apps.catalog.models import Category
    from django import forms as dj_forms

    class CategoryForm(dj_forms.ModelForm):
        class Meta:
            model = Category
            fields = ['name', 'icon', 'description', 'image', 'is_active', 'order']
            widgets = {
                'name':        dj_forms.TextInput(attrs={'class': 'form-control'}),
                'icon':        dj_forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'fa-paw'}),
                'description': dj_forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
                'order':       dj_forms.NumberInput(attrs={'class': 'form-control'}),
                'is_active':   dj_forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            }

    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Categoria "{category.name}" criada!')
            return redirect('dashboard:category_list')
    else:
        form = CategoryForm()
    return render(request, 'dashboard/management/category_form.html', {
        'form': form, 'action': 'Criar categoria'
    })


@group_required('Gerente', 'Estoquista')
def category_edit(request, pk):
    from apps.catalog.models import Category
    from django import forms as dj_forms

    class CategoryForm(dj_forms.ModelForm):
        class Meta:
            model = Category
            fields = ['name', 'icon', 'description', 'image', 'is_active', 'order']
            widgets = {
                'name':        dj_forms.TextInput(attrs={'class': 'form-control'}),
                'icon':        dj_forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'fa-paw'}),
                'description': dj_forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
                'order':       dj_forms.NumberInput(attrs={'class': 'form-control'}),
                'is_active':   dj_forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            }

    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{category.name}" atualizada!')
            return redirect('dashboard:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'dashboard/management/category_form.html', {
        'form': form, 'category': category, 'action': 'Editar categoria'
    })


@group_required('Gerente')
def category_delete(request, pk):
    from apps.catalog.models import Category
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        name = category.name
        try:
            category.delete()
            messages.success(request, f'"{name}" removida.')
        except Exception:
            messages.error(request, f'Não é possível remover "{name}": há produtos vinculados.')
        return redirect('dashboard:category_list')
    return render(request, 'dashboard/management/confirm_delete.html', {
        'object': category, 'type': 'categoria'
    })


# ══════════════════════════════════════════════════════
# PEDIDOS
# ══════════════════════════════════════════════════════

@group_required('Gerente', 'Atendimento')
def order_list_staff(request):
    from apps.orders.models import Order
    qs = Order.objects.select_related('user').order_by('-created_at')

    status = request.GET.get('status', '')
    if status:
        qs = qs.filter(status=status)

    q = request.GET.get('q', '')
    if q:
        qs = qs.filter(
            Q(order_number__icontains=q) |
            Q(user__email__icontains=q) |
            Q(user__first_name__icontains=q)
        )

    paginator = Paginator(qs, 25)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'dashboard/management/order_list.html', {
        'page_obj':       page_obj,
        'status':         status,
        'q':              q,
        'status_choices': Order.STATUS_CHOICES,
    })


@group_required('Gerente', 'Atendimento')
def order_detail_staff(request, order_number):
    from apps.orders.models import Order
    order = get_object_or_404(Order, order_number=order_number)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            old_label = order.get_status_display()
            order.status = new_status
            order.save(update_fields=['status'])
            new_label = order.get_status_display()
            messages.success(
                request,
                f'Pedido #{order_number} atualizado: {old_label} → {new_label}'
            )
            return redirect('dashboard:order_detail_staff', order_number=order_number)

    return render(request, 'dashboard/management/order_detail.html', {
        'order':          order,
        'status_choices': Order.STATUS_CHOICES,
    })


# ══════════════════════════════════════════════════════
# EVENTOS
# ══════════════════════════════════════════════════════

@group_required('Gerente', 'Marketing')
def event_list(request):
    from apps.events.models import Event
    qs = Event.objects.order_by('-start_date')
    paginator = Paginator(qs, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/management/event_list.html', {
        'page_obj': page_obj
    })


@group_required('Gerente', 'Marketing')
def event_create(request):
    from apps.events.forms import EventForm
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save()
            messages.success(request, f'Evento "{event.title}" criado!')
            return redirect('dashboard:event_list')
    else:
        form = EventForm()
    return render(request, 'dashboard/management/event_form.html', {
        'form': form, 'action': 'Criar evento'
    })


@group_required('Gerente', 'Marketing')
def event_edit(request, pk):
    from apps.events.models import Event
    from apps.events.forms import EventForm
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evento atualizado!')
            return redirect('dashboard:event_list')
    else:
        form = EventForm(instance=event)
    return render(request, 'dashboard/management/event_form.html', {
        'form': form, 'event': event, 'action': 'Editar evento'
    })


# ══════════════════════════════════════════════════════
# PLANOS
# ══════════════════════════════════════════════════════

@group_required('Gerente', 'Atendimento')
def plan_list(request):
    from apps.plans.models import ServicePlan
    plans = ServicePlan.objects.prefetch_related('features').all()
    return render(request, 'dashboard/management/plan_list.html', {'plans': plans})


@group_required('Gerente', 'Atendimento')
def userplan_list(request):
    from apps.plans.models import UserPlan
    qs = UserPlan.objects.select_related('user', 'plan', 'pet').order_by('-created_at')

    q = request.GET.get('q', '')
    if q:
        qs = qs.filter(
            Q(user__email__icontains=q) | Q(user__first_name__icontains=q)
        )

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/management/userplan_list.html', {
        'page_obj': page_obj, 'q': q
    })


# ══════════════════════════════════════════════════════
# FIDELIDADE
# ══════════════════════════════════════════════════════

@group_required('Gerente', 'Marketing', 'Atendimento')
def loyalty_list(request):
    from apps.loyalty.models import LoyaltyAccount
    qs = LoyaltyAccount.objects.select_related('user').order_by('-points')

    q = request.GET.get('q', '')
    if q:
        qs = qs.filter(
            Q(user__email__icontains=q) | Q(user__first_name__icontains=q)
        )

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/management/loyalty_list.html', {
        'page_obj': page_obj, 'q': q
    })


# ══════════════════════════════════════════════════════
# USUÁRIOS
# ══════════════════════════════════════════════════════

@group_required('Gerente')
def user_list(request):
    from apps.accounts.models import User
    qs = User.objects.prefetch_related('groups').order_by('-date_joined')

    q = request.GET.get('q', '')
    if q:
        qs = qs.filter(
            Q(email__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q)
        )

    paginator = Paginator(qs, 25)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/management/user_list.html', {
        'page_obj': page_obj, 'q': q
    })


@group_required('Gerente')
def user_edit(request, pk):
    from apps.accounts.models import User
    from django.contrib.auth.models import Group
    from apps.accounts.forms import ProfileForm
    user = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        groups    = request.POST.getlist('groups')
        is_active = request.POST.get('is_active') == 'on'
        is_staff  = request.POST.get('is_staff') == 'on'
        if form.is_valid():
            u = form.save(commit=False)
            u.is_active = is_active
            u.is_staff  = is_staff
            u.save()
            u.groups.set(Group.objects.filter(pk__in=groups))
            messages.success(request, 'Usuário atualizado!')
            return redirect('dashboard:user_list')
    else:
        form = ProfileForm(instance=user)

    return render(request, 'dashboard/management/user_edit.html', {
        'form':        form,
        'target_user': user,
        'all_groups':  Group.objects.all(),
        'user_groups': user.groups.values_list('pk', flat=True),
    })


@group_required('Gerente')
def group_list(request):
    from django.contrib.auth.models import Group
    groups = Group.objects.prefetch_related('permissions').all()
    return render(request, 'dashboard/management/group_list.html', {'groups': groups})

# ══════════════════════════════════════════════════════
# REGRAS DE FIDELIDADE
# ══════════════════════════════════════════════════════

@group_required('Gerente', 'Marketing')
def loyalty_rule_list(request):
    from apps.loyalty.models import LoyaltyRule
    qs = LoyaltyRule.objects.select_related(
        'trigger_brand', 'trigger_product', 'reward_product'
    ).order_by('-is_active', 'name')

    q = request.GET.get('q', '')
    if q:
        qs = qs.filter(name__icontains=q)

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/management/loyalty_rule_list.html', {
        'page_obj': page_obj, 'q': q,
    })


@group_required('Gerente', 'Marketing')
def loyalty_rule_create(request):
    from apps.loyalty.models import LoyaltyRule
    from django import forms as dj_forms

    class LoyaltyRuleForm(dj_forms.ModelForm):
        class Meta:
            model = LoyaltyRule
            fields = [
                'name', 'description', 'rule_type', 'reward_type',
                'trigger_brand', 'trigger_product', 'trigger_quantity', 'trigger_amount',
                'reward_product', 'reward_discount', 'reward_points',
                'is_active', 'valid_from', 'valid_until',
            ]
            widgets = {
                'name':             dj_forms.TextInput(attrs={'class': 'form-control'}),
                'description':      dj_forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
                'rule_type':        dj_forms.Select(attrs={'class': 'form-select'}),
                'reward_type':      dj_forms.Select(attrs={'class': 'form-select'}),
                'trigger_brand':    dj_forms.Select(attrs={'class': 'form-select'}),
                'trigger_product':  dj_forms.Select(attrs={'class': 'form-select'}),
                'trigger_quantity': dj_forms.NumberInput(attrs={'class': 'form-control'}),
                'trigger_amount':   dj_forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
                'reward_product':   dj_forms.Select(attrs={'class': 'form-select'}),
                'reward_discount':  dj_forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
                'reward_points':    dj_forms.NumberInput(attrs={'class': 'form-control'}),
                'valid_from':       dj_forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                'valid_until':      dj_forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                'is_active':        dj_forms.CheckboxInput(),
            }

    if request.method == 'POST':
        form = LoyaltyRuleForm(request.POST)
        if form.is_valid():
            rule = form.save()
            messages.success(request, f'Regra "{rule.name}" criada!')
            return redirect('dashboard:loyalty_rule_list')
    else:
        form = LoyaltyRuleForm()
    return render(request, 'dashboard/management/loyalty_rule_form.html', {
        'form': form, 'action': 'Criar regra'
    })


@group_required('Gerente', 'Marketing')
def loyalty_rule_edit(request, pk):
    from apps.loyalty.models import LoyaltyRule
    from django import forms as dj_forms

    class LoyaltyRuleForm(dj_forms.ModelForm):
        class Meta:
            model = LoyaltyRule
            fields = [
                'name', 'description', 'rule_type', 'reward_type',
                'trigger_brand', 'trigger_product', 'trigger_quantity', 'trigger_amount',
                'reward_product', 'reward_discount', 'reward_points',
                'is_active', 'valid_from', 'valid_until',
            ]
            widgets = {
                'name':             dj_forms.TextInput(attrs={'class': 'form-control'}),
                'description':      dj_forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
                'rule_type':        dj_forms.Select(attrs={'class': 'form-select'}),
                'reward_type':      dj_forms.Select(attrs={'class': 'form-select'}),
                'trigger_brand':    dj_forms.Select(attrs={'class': 'form-select'}),
                'trigger_product':  dj_forms.Select(attrs={'class': 'form-select'}),
                'trigger_quantity': dj_forms.NumberInput(attrs={'class': 'form-control'}),
                'trigger_amount':   dj_forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
                'reward_product':   dj_forms.Select(attrs={'class': 'form-select'}),
                'reward_discount':  dj_forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
                'reward_points':    dj_forms.NumberInput(attrs={'class': 'form-control'}),
                'valid_from':       dj_forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                'valid_until':      dj_forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                'is_active':        dj_forms.CheckboxInput(),
            }

    rule = get_object_or_404(LoyaltyRule, pk=pk)
    if request.method == 'POST':
        form = LoyaltyRuleForm(request.POST, instance=rule)
        if form.is_valid():
            form.save()
            messages.success(request, f'Regra "{rule.name}" atualizada!')
            return redirect('dashboard:loyalty_rule_list')
    else:
        form = LoyaltyRuleForm(instance=rule)
    return render(request, 'dashboard/management/loyalty_rule_form.html', {
        'form': form, 'rule': rule, 'action': 'Editar regra'
    })


@group_required('Gerente')
def loyalty_rule_delete(request, pk):
    from apps.loyalty.models import LoyaltyRule
    rule = get_object_or_404(LoyaltyRule, pk=pk)
    if request.method == 'POST':
        name = rule.name
        rule.delete()
        messages.success(request, f'Regra "{name}" removida.')
        return redirect('dashboard:loyalty_rule_list')
    return render(request, 'dashboard/management/confirm_delete.html', {
        'object': rule, 'type': 'regra de fidelidade'
    })