from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.db.models import Sum, Count, Q
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
        created_at__date=today, status__in=['confirmed', 'preparing', 'ready', 'shipped', 'delivered']
    ).aggregate(total=Sum('total'))['total'] or 0

    revenue_month = Order.objects.filter(
        created_at__date__gte=month_ago, status__in=['confirmed', 'preparing', 'ready', 'shipped', 'delivered']
    ).aggregate(total=Sum('total'))['total'] or 0

    low_stock = Stock.objects.filter(quantity__lte=models_min_qty()).select_related('product')[:10]
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
    new_users = User.objects.filter(date_joined__date__gte=week_ago).count()
    open_cash = CashRegister.objects.filter(status='open').first()

    return render(request, 'dashboard/home.html', {
        'total_orders_today': total_orders_today,
        'revenue_today': revenue_today,
        'revenue_month': revenue_month,
        'low_stock': low_stock,
        'recent_orders': recent_orders,
        'new_users': new_users,
        'open_cash': open_cash,
    })


def models_min_qty():
    from django.db.models import F
    return F('min_quantity')


@staff_member_required
def stock_view(request):
    from apps.catalog.models import Stock
    status_filter = request.GET.get('status', 'all')

    stocks = Stock.objects.select_related(
        'product__category', 'product__brand'
    ).order_by('quantity')

    if status_filter == 'low':
        # Estoque baixo mas não zerado
        stocks = [s for s in stocks if s.is_low and not s.is_out]
    elif status_filter == 'out':
        stocks = [s for s in stocks if s.is_out]

    return render(request, 'dashboard/stock.html', {
        'stocks': stocks,
        'status_filter': status_filter,
    })


@staff_member_required
def stock_movement_create(request, product_id):
    from apps.catalog.models import Product
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
def order_management_view(request):
    status_filter = request.GET.get('status', '')
    orders = Order.objects.select_related('user').order_by('-created_at')
    if status_filter:
        orders = orders.filter(status=status_filter)
    return render(request, 'dashboard/orders.html', {
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES,
        'selected_status': status_filter,
    })


@staff_member_required
def update_order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.status = request.POST.get('status')
        order.save()
    return redirect('dashboard:orders')