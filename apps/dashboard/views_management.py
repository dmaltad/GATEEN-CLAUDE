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
from django.http import JsonResponse


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
    now       = timezone.now()
    month_ago = today - timedelta(days=30)
    week_ago  = today - timedelta(days=7)

    paid_statuses = ['confirmed', 'preparing', 'ready', 'shipped', 'delivered']

    # ── Pedidos ───────────────────────────────────────────────
    total_orders_today = Order.objects.filter(created_at__date=today).count()
    revenue_today = (
        Order.objects.filter(created_at__date=today, status__in=paid_statuses)
        .aggregate(total=Sum('total'))['total'] or 0
    )
    revenue_month = (
        Order.objects.filter(created_at__date__gte=month_ago, status__in=paid_statuses)
        .aggregate(total=Sum('total'))['total'] or 0
    )
    pending_orders = Order.objects.filter(status='pending').count()

    # ── Usuários ──────────────────────────────────────────────
    new_users       = User.objects.filter(date_joined__date__gte=week_ago).count()
    total_customers = User.objects.filter(is_staff=False).count()

    # ── Estoque ───────────────────────────────────────────────
    low_stock = (
        Stock.objects.filter(quantity__lte=5)
        .select_related('product')[:8]
    )
    low_stock_count = Stock.objects.filter(quantity__lte=5).count()
    out_stock_count = Stock.objects.filter(quantity__lte=0).count()

    # ── Agendamentos ──────────────────────────────────────────
    appt_today      = 0
    appt_week       = 0
    appt_pending    = 0
    upcoming_appts  = []
    week_start = today
    week_end   = today + timedelta(days=7)

    try:
        from apps.appointments.models import Appointment
        appt_today   = Appointment.objects.filter(
            scheduled_at__date=today,
            status__in=['pending', 'confirmed']
        ).count()
        appt_week    = Appointment.objects.filter(
            scheduled_at__date__gte=today,
            scheduled_at__date__lte=week_end,
            status__in=['pending', 'confirmed']
        ).count()
        appt_pending = Appointment.objects.filter(status='pending').count()
        upcoming_appts = (
            Appointment.objects
            .filter(
                scheduled_at__date__gte=today,
                scheduled_at__date__lte=week_end,
                status__in=['pending', 'confirmed'],
            )
            .select_related('pet', 'user', 'user_plan__plan')
            .order_by('scheduled_at')[:8]
        )
    except Exception:
        pass

    # ── Eventos ───────────────────────────────────────────────
    active_events = Event.objects.filter(
        is_active=True,
        start_date__gte=now - timedelta(days=1),
    ).order_by('start_date')[:5]

    # ── Pedidos recentes ──────────────────────────────────────
    recent_orders = (
        Order.objects.select_related('user')
        .order_by('-created_at')[:8]
    )

    # ── Atalhos ───────────────────────────────────────────────
    shortcuts = [
        {'label': 'Produtos',        'icon': 'fa-box',           'color': '#8A4B9F', 'url': '/dashboard/gestao/produtos/'},
        {'label': 'Categorias',      'icon': 'fa-th',            'color': '#795548', 'url': '/dashboard/gestao/categorias/'},
        {'label': 'Pedidos',         'icon': 'fa-shopping-cart', 'color': '#E74C3C', 'url': '/dashboard/gestao/pedidos/'},
        {'label': 'Agendamentos',    'icon': 'fa-cut',           'color': '#00897B', 'url': '/dashboard/gestao/agendamentos/'},
        {'label': 'Eventos',         'icon': 'fa-calendar',      'color': '#F4B942', 'url': '/dashboard/gestao/eventos/'},
        {'label': 'Planos',          'icon': 'fa-star',          'color': '#FF9800', 'url': '/dashboard/gestao/planos/'},
        {'label': 'Planos ativos',   'icon': 'fa-id-card',       'color': '#009688', 'url': '/dashboard/gestao/planos/ativos/'},
        {'label': 'Fidelidade',      'icon': 'fa-gift',          'color': '#9C27B0', 'url': '/dashboard/gestao/fidelidade/'},
        {'label': 'Regras fidel.',   'icon': 'fa-award',         'color': '#7B1FA2', 'url': '/dashboard/gestao/fidelidade/regras/'},
        {'label': 'Usuários',        'icon': 'fa-users',         'color': '#2196F3', 'url': '/dashboard/gestao/usuarios/'},
        {'label': 'Cargos',          'icon': 'fa-user-tag',      'color': '#607D8B', 'url': '/dashboard/gestao/cargos/'},
    ]

    return render(request, 'dashboard/home.html', {
        # Pedidos
        'total_orders_today': total_orders_today,
        'pending_orders':     pending_orders,
        'revenue_today':      revenue_today,
        'revenue_month':      revenue_month,
        # Usuários
        'new_users':          new_users,
        'total_customers':    total_customers,
        # Estoque
        'low_stock':          low_stock,
        'low_stock_count':    low_stock_count,
        'out_stock_count':    out_stock_count,
        # Agendamentos
        'appt_today':         appt_today,
        'appt_week':          appt_week,
        'appt_pending':       appt_pending,
        'upcoming_appts':     upcoming_appts,
        # Eventos
        'active_events':      active_events,
        # Pedidos
        'recent_orders':      recent_orders,
        # Atalhos
        'shortcuts':          shortcuts,
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

# ══════════════════════════════════════════════════════
# PLANOS DE SERVIÇO — CRUD
# ══════════════════════════════════════════════════════

@group_required('Gerente')
def plan_create(request):
    from apps.plans.models import ServicePlan, PlanFeature
    from django import forms as dj_forms

    class ServicePlanForm(dj_forms.ModelForm):
        class Meta:
            model = ServicePlan
            fields = [
                'name', 'description', 'price', 'period',
                'food_bags_per_month', 'grooming_sessions_per_month',
                'includes_health_plan', 'health_plan_details',
                'color', 'order', 'is_active', 'is_featured',
            ]
            widgets = {
                'name':                         dj_forms.TextInput(attrs={'class': 'form-control'}),
                'description':                  dj_forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
                'price':                        dj_forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
                'period':                       dj_forms.Select(attrs={'class': 'form-select'}),
                'food_bags_per_month':          dj_forms.NumberInput(attrs={'class': 'form-control'}),
                'grooming_sessions_per_month':  dj_forms.NumberInput(attrs={'class': 'form-control'}),
                'health_plan_details':          dj_forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
                'color':                        dj_forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
                'order':                        dj_forms.NumberInput(attrs={'class': 'form-control'}),
                'includes_health_plan':         dj_forms.CheckboxInput(),
                'is_active':                    dj_forms.CheckboxInput(),
                'is_featured':                  dj_forms.CheckboxInput(),
            }

    if request.method == 'POST':
        form = ServicePlanForm(request.POST)
        features_raw = request.POST.get('features_text', '').strip()
        if form.is_valid():
            from django.utils.text import slugify
            plan = form.save(commit=False)
            base = slugify(plan.name)
            plan.slug = base
            n = 1
            while ServicePlan.objects.filter(slug=plan.slug).exists():
                plan.slug = f'{base}-{n}'
                n += 1
            plan.save()
            if features_raw:
                for line in features_raw.splitlines():
                    line = line.strip()
                    if line:
                        PlanFeature.objects.create(plan=plan, description=line)
            messages.success(request, f'Plano "{plan.name}" criado!')
            return redirect('dashboard:plan_list')
    else:
        form = ServicePlanForm()
    return render(request, 'dashboard/management/plan_form.html', {
        'form': form, 'action': 'Criar plano'
    })


@group_required('Gerente')
def plan_edit(request, pk):
    from apps.plans.models import ServicePlan, PlanFeature
    from django import forms as dj_forms

    class ServicePlanForm(dj_forms.ModelForm):
        class Meta:
            model = ServicePlan
            fields = [
                'name', 'description', 'price', 'period',
                'food_bags_per_month', 'grooming_sessions_per_month',
                'includes_health_plan', 'health_plan_details',
                'color', 'order', 'is_active', 'is_featured',
            ]
            widgets = {
                'name':                         dj_forms.TextInput(attrs={'class': 'form-control'}),
                'description':                  dj_forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
                'price':                        dj_forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
                'period':                       dj_forms.Select(attrs={'class': 'form-select'}),
                'food_bags_per_month':          dj_forms.NumberInput(attrs={'class': 'form-control'}),
                'grooming_sessions_per_month':  dj_forms.NumberInput(attrs={'class': 'form-control'}),
                'health_plan_details':          dj_forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
                'color':                        dj_forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
                'order':                        dj_forms.NumberInput(attrs={'class': 'form-control'}),
                'includes_health_plan':         dj_forms.CheckboxInput(),
                'is_active':                    dj_forms.CheckboxInput(),
                'is_featured':                  dj_forms.CheckboxInput(),
            }

    plan = get_object_or_404(ServicePlan, pk=pk)
    if request.method == 'POST':
        form = ServicePlanForm(request.POST, instance=plan)
        features_raw = request.POST.get('features_text', '').strip()
        if form.is_valid():
            form.save()
            # Recria os benefícios se o campo foi enviado
            if features_raw:
                plan.features.all().delete()
                for line in features_raw.splitlines():
                    line = line.strip()
                    if line:
                        PlanFeature.objects.create(plan=plan, description=line)
            messages.success(request, f'Plano "{plan.name}" atualizado!')
            return redirect('dashboard:plan_list')
    else:
        form = ServicePlanForm(instance=plan)

    features_text = '\n'.join(plan.features.values_list('description', flat=True))
    return render(request, 'dashboard/management/plan_form.html', {
        'form': form, 'plan': plan,
        'features_text': features_text,
        'action': 'Editar plano',
    })


@group_required('Gerente')
def plan_delete(request, pk):
    from apps.plans.models import ServicePlan
    plan = get_object_or_404(ServicePlan, pk=pk)
    if request.method == 'POST':
        name = plan.name
        try:
            plan.delete()
            messages.success(request, f'Plano "{name}" removido.')
        except Exception:
            messages.error(request, f'Não é possível remover "{name}": há assinantes ativos.')
        return redirect('dashboard:plan_list')
    return render(request, 'dashboard/management/confirm_delete.html', {
        'object': plan, 'type': 'plano'
    })

# ══════════════════════════════════════════════════════
# AGENDAMENTOS — GESTÃO STAFF
# ══════════════════════════════════════════════════════

@group_required('Gerente', 'Atendimento')
def appointment_list_staff(request):
    from apps.appointments.models import Appointment

    qs = (
        Appointment.objects
        .select_related('user', 'pet', 'user_plan__plan')
        .order_by('scheduled_at')
    )

    # Filtros
    status = request.GET.get('status', '')
    if status:
        qs = qs.filter(status=status)

    date_str = request.GET.get('date', '')
    if date_str:
        qs = qs.filter(scheduled_at__date=date_str)

    q = request.GET.get('q', '')
    if q:
        qs = qs.filter(
            Q(user__email__icontains=q)    |
            Q(user__first_name__icontains=q) |
            Q(pet__name__icontains=q)
        )

    # Padrão: só futuros/hoje; se filtrar por status, mostra todos
    if not status and not date_str:
        qs = qs.filter(scheduled_at__date__gte=timezone.now().date())

    paginator = Paginator(qs, 25)
    page_obj  = paginator.get_page(request.GET.get('page'))

    return render(request, 'dashboard/management/appointment_list.html', {
        'page_obj':       page_obj,
        'status':         status,
        'date_filter':    date_str,
        'q':              q,
        'status_choices': [
            ('pending',   'Pendente'),
            ('confirmed', 'Confirmado'),
            ('done',      'Concluído'),
            ('cancelled', 'Cancelado'),
        ],
    })


@group_required('Gerente', 'Atendimento')
def appointment_update_status(request, pk):
    from apps.appointments.models import Appointment
    from apps.appointments.services import cancel_appointment as svc_cancel

    appt       = get_object_or_404(Appointment, pk=pk)
    new_status = request.POST.get('status', '')
    allowed    = {'pending', 'confirmed', 'done', 'cancelled'}

    if request.method == 'POST' and new_status in allowed:
        old_label = appt.get_status_display()

        if new_status == 'cancelled':
            svc_cancel(appt)          # devolve sessão ao plano se necessário
        else:
            appt.status = new_status
            appt.save(update_fields=['status'])

        new_label = appt.get_status_display()
        messages.success(
            request,
            f'Agendamento #{appt.pk} ({appt.pet.name}): '
            f'{old_label} → {new_label}'
        )
    else:
        messages.error(request, 'Status inválido.')

    return redirect('dashboard:appointment_list_staff')

# ══════════════════════════════════════════════════════
# USUÁRIO — DELETE
# ══════════════════════════════════════════════════════

@group_required('Gerente')
def user_delete(request, pk):
    from apps.accounts.models import User
    user = get_object_or_404(User, pk=pk)

    # Impede excluir a si mesmo ou superusuários
    if user == request.user:
        messages.error(request, 'Você não pode excluir sua própria conta.')
        return redirect('dashboard:user_list')
    if user.is_superuser:
        messages.error(request, 'Não é possível excluir um superusuário.')
        return redirect('dashboard:user_list')

    if request.method == 'POST':
        nome = user.get_full_name()
        user.delete()
        messages.success(request, f'Usuário "{nome}" removido.')
        return redirect('dashboard:user_list')

    return render(request, 'dashboard/management/confirm_delete.html', {
        'object': user, 'type': 'usuário'
    })


# ══════════════════════════════════════════════════════
# CARGOS — CREATE / DELETE
# ══════════════════════════════════════════════════════

@group_required('Gerente')
def group_create(request):
    from django.contrib.auth.models import Group, Permission
    from django import forms as dj_forms

    class GroupForm(dj_forms.Form):
        name = dj_forms.CharField(
            max_length=150,
            label='Nome do cargo',
            widget=dj_forms.TextInput(attrs={'class': 'form-control'}),
        )
        permissions = dj_forms.ModelMultipleChoiceField(
            queryset=Permission.objects.select_related('content_type').order_by(
                'content_type__app_label', 'codename'
            ),
            required=False,
            label='Permissões',
            widget=dj_forms.CheckboxSelectMultiple(),
        )

    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            if Group.objects.filter(name=name).exists():
                form.add_error('name', 'Já existe um cargo com este nome.')
            else:
                group = Group.objects.create(name=name)
                group.permissions.set(form.cleaned_data['permissions'])
                messages.success(request, f'Cargo "{name}" criado!')
                return redirect('dashboard:group_list')
    else:
        form = GroupForm()

    return render(request, 'dashboard/management/group_form.html', {
        'form': form, 'action': 'Criar cargo'
    })


@group_required('Gerente')
def group_delete(request, pk):
    from django.contrib.auth.models import Group
    group = get_object_or_404(Group, pk=pk)

    # Protege os grupos base do sistema
    PROTECTED = {'Gerente', 'Estoquista', 'Atendimento', 'Marketing'}
    if group.name in PROTECTED:
        messages.error(
            request,
            f'O cargo "{group.name}" é padrão do sistema e não pode ser removido.'
        )
        return redirect('dashboard:group_list')

    if request.method == 'POST':
        name = group.name
        group.delete()
        messages.success(request, f'Cargo "{name}" removido.')
        return redirect('dashboard:group_list')

    return render(request, 'dashboard/management/confirm_delete.html', {
        'object': group, 'type': 'cargo'
    })

# ══════════════════════════════════════════════════════
# AGENDAMENTO — CRIAÇÃO PELO STAFF
# ══════════════════════════════════════════════════════

@group_required('Gerente', 'Atendimento')
def appointment_create_staff(request):
    from apps.accounts.models import User, Pet, Address
    from apps.appointments.models import Appointment
    from apps.appointments.services import create_appointment as svc_create
    from django.utils import timezone
    from datetime import datetime
    import uuid

    if request.method == 'POST':
        client_id     = request.POST.get('client_id', '').strip()
        pet_id        = request.POST.get('pet_id', '').strip()
        service       = request.POST.get('service', '').strip()
        scheduled_str = request.POST.get('scheduled_at', '').strip()
        notes         = request.POST.get('notes', '').strip()

        # ── Resolve ou cria cliente ───────────────────────────
        if client_id:
            try:
                client = User.objects.get(pk=client_id, is_staff=False)
            except User.DoesNotExist:
                messages.error(request, 'Cliente não encontrado.')
                return redirect('dashboard:appointment_create_staff')
        else:
            first_name  = request.POST.get('new_first_name', '').strip()
            last_name   = request.POST.get('new_last_name', '').strip()
            phone       = request.POST.get('new_phone', '').strip()
            email       = request.POST.get('new_email', '').strip()
            birth_date  = request.POST.get('new_birth_date', '') or None
            staff_notes = request.POST.get('new_staff_notes', '').strip()

            if not first_name or not last_name:
                messages.error(request, 'Nome e sobrenome são obrigatórios.')
                return redirect('dashboard:appointment_create_staff')

            # Valida email se informado
            if email and User.objects.filter(email=email).exists():
                messages.error(request, f'Já existe um cadastro com o e-mail "{email}".')
                return redirect('dashboard:appointment_create_staff')

            # Gera email placeholder se não informado
            final_email = email if email else (
                f'walkin_{phone.replace(" ","").replace("-","").replace("(","").replace(")","")}'
                f'_{uuid.uuid4().hex[:8]}@gateen.internal'
            )

            client = User(
                email=final_email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                birth_date=birth_date,
                is_walk_in=True,
                is_active=True,
                is_staff=False,
                staff_notes=staff_notes,
            )
            client.set_unusable_password()
            client.save()

            # Cria endereço se os campos essenciais foram informados
            cep          = request.POST.get('new_cep', '').strip()
            street       = request.POST.get('new_street', '').strip()
            number       = request.POST.get('new_number', '').strip()
            neighborhood = request.POST.get('new_neighborhood', '').strip()
            city         = request.POST.get('new_city', '').strip()
            state        = request.POST.get('new_state', '').strip()

            if cep and street and city:
                Address.objects.create(
                    user=client,
                    label='Principal',
                    cep=cep,
                    street=street,
                    number=number or 'S/N',
                    complement='',
                    neighborhood=neighborhood,
                    city=city,
                    state=state,
                    is_default=True,
                )

        # ── Resolve ou cria pet ───────────────────────────────
        if pet_id:
            try:
                pet = Pet.objects.get(pk=pet_id, owner=client)
            except Pet.DoesNotExist:
                messages.error(request, 'Pet não encontrado para este cliente.')
                return redirect('dashboard:appointment_create_staff')
        else:
            pet_name    = request.POST.get('new_pet_name', '').strip()
            pet_species = request.POST.get('new_pet_species', 'dog')
            pet_breed   = request.POST.get('new_pet_breed', '').strip()
            pet_size    = request.POST.get('new_pet_size', '')

            if not pet_name:
                messages.error(request, 'Nome do pet é obrigatório.')
                return redirect('dashboard:appointment_create_staff')

            pet = Pet.objects.create(
                owner=client,
                name=pet_name,
                species=pet_species,
                breed=pet_breed,
                size=pet_size,
            )

        # ── Cria o agendamento ────────────────────────────────
        if not service or not scheduled_str:
            messages.error(request, 'Serviço e data/hora são obrigatórios.')
            return redirect('dashboard:appointment_create_staff')

        try:
            naive_dt     = datetime.fromisoformat(scheduled_str)
            scheduled_at = timezone.make_aware(naive_dt)
        except ValueError:
            messages.error(request, 'Data/hora inválida.')
            return redirect('dashboard:appointment_create_staff')

        appt, used_plan, plan = svc_create(
            user=client,
            pet=pet,
            service=service,
            scheduled_at=scheduled_at,
            notes=notes,
        )

        msg = (
            f'Agendamento #{appt.pk} criado para {client.get_full_name()} '
            f'({pet.name}) em {scheduled_at.strftime("%d/%m/%Y às %H:%M")}!'
        )
        if used_plan:
            msg += f' (1 sessão descontada do plano {plan.plan.name})'
        messages.success(request, msg)
        return redirect('dashboard:appointment_list_staff')

    from apps.appointments.models import Appointment
    return render(request, 'dashboard/management/appointment_create.html', {
        'service_choices': Appointment.SERVICE_CHOICES,
        'species_choices': Pet.SPECIES_CHOICES,
        'size_choices':    Pet.SIZE_CHOICES,
    })


@group_required('Gerente', 'Atendimento')
def client_search_ajax(request):
    from apps.accounts.models import User
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})

    qs = User.objects.filter(
        Q(first_name__icontains=q) |
        Q(last_name__icontains=q) |
        Q(email__icontains=q) |
        Q(phone__icontains=q)
    ).filter(is_staff=False).prefetch_related('pets')[:10]

    results = []
    for u in qs:
        email_display = '' if u.email.endswith('@gateen.internal') else u.email
        results.append({
            'id':         u.pk,
            'name':       u.get_full_name(),
            'email':      email_display,
            'phone':      u.phone,
            'is_walk_in': getattr(u, 'is_walk_in', False),
            'pet_count':  u.pets.count(),
        })

    return JsonResponse({'results': results})


@group_required('Gerente', 'Atendimento')
def client_pets_ajax(request, pk):
    from apps.accounts.models import User
    try:
        client = User.objects.prefetch_related('pets').get(pk=pk, is_staff=False)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Cliente não encontrado'}, status=404)

    pets = [{
        'id':      p.pk,
        'name':    p.name,
        'species': p.get_species_display(),
        'breed':   p.breed or '—',
        'size':    p.get_size_display() if p.size else '—',
    } for p in client.pets.all()]

    email_display = '' if client.email.endswith('@gateen.internal') else client.email
    return JsonResponse({
        'client_id':   client.pk,
        'client_name': client.get_full_name(),
        'client_phone': client.phone,
        'client_email': email_display,
        'is_walk_in':  getattr(client, 'is_walk_in', False),
        'pets':        pets,
    })


@group_required('Gerente', 'Atendimento')
def client_send_invite(request, pk):
    from apps.accounts.models import User
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string
    from django.conf import settings

    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)

    try:
        client = User.objects.get(pk=pk, is_staff=False)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Cliente não encontrado'}, status=404)

    if not client.email or client.email.endswith('@gateen.internal'):
        return JsonResponse(
            {'error': 'Este cliente não possui e-mail válido cadastrado.'},
            status=400,
        )
    
    from django.urls import reverse
    uid   = urlsafe_base64_encode(force_bytes(client.pk))
    token = default_token_generator.make_token(client)
    invite_url = request.build_absolute_uri(
        reverse('accounts:complete_registration',
                kwargs={'uidb64': uid, 'token': token})
    )

    context = {
        'client_name': client.get_full_name(),
        'invite_url':  invite_url,
        'site_name':   'Gateen Petshop',
    }

    try:
        html_body = render_to_string(
            'accounts/email/invite_complete_registration.html', context
        )
        text_body = (
            f'Olá {client.get_full_name()},\n\n'
            f'Você foi cadastrado na Gateen Petshop.\n'
            f'Para criar sua senha e acessar sua conta, clique no link abaixo:\n\n'
            f'{invite_url}\n\n'
            f'O link é válido por 24 horas.\n\n'
            f'— Equipe Gateen Petshop'
        )
        msg = EmailMultiAlternatives(
            subject='Complete seu cadastro — Gateen Petshop',
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[client.email],
        )
        msg.attach_alternative(html_body, 'text/html')
        msg.send()
        return JsonResponse({
            'success': True,
            'message': f'Convite enviado para {client.email}'
        })
    except Exception as exc:
        return JsonResponse({'error': f'Falha no envio: {str(exc)}'}, status=500)
    
# ══════════════════════════════════════════════════════
# PEDIDOS — CRIAÇÃO PELO STAFF
# ══════════════════════════════════════════════════════

@group_required('Gerente', 'Atendimento')
def order_create_staff(request):
    from apps.accounts.models import User, Address
    from apps.catalog.models import Product
    from apps.orders.models import Order, OrderItem
    from django.db import transaction as db_transaction
    from django.db.models import F as Fexpr
    import json

    if request.method == 'POST':
        client_id      = request.POST.get('client_id', '').strip()
        items_json     = request.POST.get('items_json', '[]').strip()
        delivery_type  = request.POST.get('delivery_type', 'pickup')
        payment_method = request.POST.get('payment_method', 'cash')
        address_id     = request.POST.get('address_id', '').strip()
        notes          = request.POST.get('notes', '').strip()
        discount_str   = request.POST.get('discount', '0').strip()

        # ── Resolve cliente ─────────────────────────────────
        if not client_id:
            messages.error(request, 'Selecione um cliente.')
            return redirect('dashboard:order_create_staff')

        try:
            client = User.objects.get(pk=client_id, is_staff=False)
        except User.DoesNotExist:
            messages.error(request, 'Cliente não encontrado.')
            return redirect('dashboard:order_create_staff')

        # ── Parse itens ──────────────────────────────────────
        try:
            items_data = json.loads(items_json)
        except (json.JSONDecodeError, ValueError):
            messages.error(request, 'Erro ao processar os produtos do pedido.')
            return redirect('dashboard:order_create_staff')

        if not items_data:
            messages.error(request, 'Adicione pelo menos um produto ao pedido.')
            return redirect('dashboard:order_create_staff')

        # ── Parse desconto ───────────────────────────────────
        try:
            discount = max(0.0, float(discount_str))
        except ValueError:
            discount = 0.0

        # ── Resolve endereço ─────────────────────────────────
        address = None
        if delivery_type == 'delivery' and address_id:
            try:
                address = Address.objects.get(pk=address_id, user=client)
            except Address.DoesNotExist:
                pass

        # ── Resolve produtos e calcula subtotal ──────────────
        resolved_items = []
        subtotal = 0

        for row in items_data:
            try:
                product = Product.objects.select_related('stock').get(
                    pk=row['product_id'], is_active=True
                )
                qty   = max(1, int(row.get('quantity', 1)))
                price = product.current_price
                subtotal += price * qty
                resolved_items.append((product, qty, price))
            except (Product.DoesNotExist, KeyError, ValueError, TypeError):
                messages.error(request, 'Um ou mais produtos são inválidos.')
                return redirect('dashboard:order_create_staff')

        delivery_fee = 10 if delivery_type == 'delivery' else 0
        discount     = min(discount, float(subtotal))
        total        = float(subtotal) + delivery_fee - discount

        # ── Cria o pedido ────────────────────────────────────
        try:
            with db_transaction.atomic():
                order = Order.objects.create(
                    user=client,
                    delivery_type=delivery_type,
                    payment_method=payment_method,
                    address=address,
                    subtotal=subtotal,
                    discount=discount,
                    delivery_fee=delivery_fee,
                    total=total,
                    notes=notes,
                    status='confirmed',   # pedidos manuais já confirmados
                )

                for product, qty, price in resolved_items:
                    if product.stock.quantity < qty:
                        raise ValueError(
                            f'Estoque insuficiente para "{product.name}" '
                            f'({product.stock.quantity} un. disponíveis).'
                        )
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=qty,
                        unit_price=price,
                    )
                    product.stock.quantity = Fexpr('quantity') - qty
                    product.stock.save(update_fields=['quantity'])

            messages.success(
                request,
                f'Pedido #{order.order_number} criado para '
                f'{client.get_full_name()} · Total: R$ {total:.2f}'
            )
            return redirect('dashboard:order_detail_staff',
                            order_number=order.order_number)

        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect('dashboard:order_create_staff')
        except Exception:
            messages.error(request, 'Erro inesperado. Tente novamente.')
            return redirect('dashboard:order_create_staff')

    return render(request, 'dashboard/management/order_create.html', {
        'payment_choices':  Order.PAYMENT_CHOICES,
        'delivery_choices': Order.DELIVERY_CHOICES,
    })


@group_required('Gerente', 'Atendimento')
def product_search_staff_ajax(request):
    from apps.catalog.models import Product
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})

    products = Product.objects.filter(
        Q(name__icontains=q) | Q(brand__name__icontains=q),
        is_active=True,
    ).select_related('brand', 'category', 'stock')[:12]

    results = []
    for p in products:
        stock_qty = p.stock.quantity if hasattr(p, 'stock') and p.stock else 0
        results.append({
            'id':       p.pk,
            'name':     p.name,
            'brand':    p.brand.name if p.brand else '',
            'category': p.category.name,
            'price':    float(p.current_price),
            'price_display': f'R$ {p.current_price:.2f}'.replace('.', ','),
            'stock':    stock_qty,
            'image':    p.image.url if p.image and p.image.name else None,
        })

    return JsonResponse({'results': results})