from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages  # ← FALTAVA ESTE IMPORT
from django.utils import timezone
from django.db.models import Sum, Count, Q, F
from apps.orders.models import Order, CashRegister, CashTransaction
from apps.catalog.models import Product, Stock, StockMovement
from apps.accounts.models import User
from datetime import timedelta


@staff_member_required
def dashboard_home(request):
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    total_orders_today = Order.objects.filter(created_at__date=today).count()
    revenue_today = Order.objects.filter(
        created_at__date=today,
        status__in=['confirmed', 'preparing', 'ready', 'shipped', 'delivered']
    ).aggregate(total=Sum('total'))['total'] or 0

    revenue_month = Order.objects.filter(
        created_at__date__gte=month_ago,
        status__in=['confirmed', 'preparing', 'ready', 'shipped', 'delivered']
    ).aggregate(total=Sum('total'))['total'] or 0

    low_stock = Stock.objects.filter(
        quantity__lte=F('min_quantity')
    ).select_related('product')[:10]

    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
    new_users = User.objects.filter(date_joined__date__gte=week_ago).count()
    open_cash = CashRegister.objects.filter(status='open').first()

    shortcuts = [
        {'label': 'Produtos',   'icon': 'fa-box',           'color': '#8A4B9F', 'url': '/dashboard/gestao/produtos/'},
        {'label': 'Estoque',    'icon': 'fa-cubes',         'color': '#3498DB', 'url': '/dashboard/estoque/'},
        {'label': 'Pedidos',    'icon': 'fa-shopping-cart', 'color': '#E74C3C', 'url': '/dashboard/pedidos/'},
        {'label': 'Caixa',      'icon': 'fa-cash-register', 'color': '#27AE60', 'url': '/dashboard/caixa/'},
        {'label': 'Eventos',    'icon': 'fa-calendar',      'color': '#F4B942', 'url': '/dashboard/gestao/eventos/'},
        {'label': 'Planos',     'icon': 'fa-star',          'color': '#FF9800', 'url': '/dashboard/gestao/planos/'},
        {'label': 'Fidelidade', 'icon': 'fa-gift',          'color': '#9C27B0', 'url': '/dashboard/gestao/fidelidade/'},
        {'label': 'Categorias', 'icon': 'fa-th',            'color': '#607D8B', 'url': '/admin/catalog/category/'},
        {'label': 'Usuários',   'icon': 'fa-users',         'color': '#2196F3', 'url': '/dashboard/gestao/usuarios/'},
    ]

    return render(request, 'dashboard/home.html', {
        'total_orders_today': total_orders_today,
        'revenue_today': revenue_today,
        'revenue_month': revenue_month,
        'low_stock': low_stock,
        'recent_orders': recent_orders,
        'new_users': new_users,
        'open_cash': open_cash,
        'shortcuts': shortcuts,
    })


@staff_member_required
def stock_view(request):
    status_filter = request.GET.get('status', 'all')

    stocks = Stock.objects.select_related(
        'product__category', 'product__brand'
    ).order_by('quantity')

    if status_filter == 'low':
        stocks = [s for s in stocks if s.is_low and not s.is_out]
    elif status_filter == 'out':
        stocks = [s for s in stocks if s.is_out]

    return render(request, 'dashboard/stock.html', {
        'stocks': stocks,
        'status_filter': status_filter,
    })


@staff_member_required
def stock_movement_create(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        movement_type = request.POST.get('movement_type')
        quantity = int(request.POST.get('quantity', 0))
        reason = request.POST.get('reason', '')
        stock, _ = Stock.objects.get_or_create(product=product)

        if movement_type == 'in':
            stock.quantity += quantity
        elif movement_type == 'out':
            stock.quantity = max(0, stock.quantity - quantity)
        elif movement_type == 'adjustment':
            stock.quantity = quantity
        stock.save()

        StockMovement.objects.create(
            product=product,
            movement_type=movement_type,
            quantity=quantity,
            current_stock=stock.quantity,
            reason=reason,
            created_by=request.user,
        )
        return redirect('dashboard:stock')

    return render(request, 'dashboard/stock_movement_form.html', {'product': product})


@staff_member_required
def cash_register_view(request):
    open_cash = CashRegister.objects.filter(status='open').first()
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'open' and not open_cash:
            CashRegister.objects.create(
                opened_by=request.user,
                opening_balance=request.POST.get('opening_balance', 0),
            )
        elif action == 'close' and open_cash:
            open_cash.status = 'closed'
            open_cash.closing_balance = request.POST.get('closing_balance', 0)
            open_cash.closed_by = request.user
            open_cash.closed_at = timezone.now()
            open_cash.save()
        return redirect('dashboard:cash_register')

    transactions = []
    if open_cash:
        transactions = open_cash.transactions.order_by('-created_at')

    return render(request, 'dashboard/cash_register.html', {
        'open_cash': open_cash,
        'transactions': transactions,
    })


@staff_member_required
def orders_view(request):
    status_filter = request.GET.get('status', '')
    q = request.GET.get('q', '')

    orders = Order.objects.select_related('user').order_by('-created_at')

    if status_filter:
        orders = orders.filter(status=status_filter)
    if q:
        orders = orders.filter(
            Q(order_number__icontains=q) |
            Q(user__email__icontains=q) |
            Q(user__first_name__icontains=q)
        )

    return render(request, 'dashboard/orders.html', {
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES,
        'selected_status': status_filter,
        'q': q,
    })


@staff_member_required
def order_detail_staff_redirect(request, order_number):
    """Atualiza status do pedido via POST e redireciona de volta."""
    order = get_object_or_404(Order, order_number=order_number)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save(update_fields=['status'])
            messages.success(
                request,
                f'Pedido #{order_number} → "{order.get_status_display()}"'
            )
    return redirect('dashboard:orders')


# Alias mantido para compatibilidade com templates antigos
update_order_status = order_detail_staff_redirect