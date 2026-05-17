from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum, F
from .models import Cart, CartItem, Order, OrderItem
from apps.catalog.models import Product


# ── Helpers ──────────────────────────────────────────────────────

def _get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(
            session_key=request.session.session_key,
            user__isnull=True,
        )
    return cart


def _cart_count(cart):
    return cart.items.aggregate(total=Sum('quantity'))['total'] or 0


# ── Cart Views ────────────────────────────────────────────────────

def cart_view(request):
    cart = _get_or_create_cart(request)
    return render(request, 'orders/cart.html', {'cart': cart})


@require_POST
def add_to_cart(request, product_id):
    from django.db.models import Q
    product = get_object_or_404(
        Product, pk=product_id, is_active=True
    )
    # Bloqueia produto sem estoque
    if hasattr(product, 'stock') and product.stock.quantity <= 0:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Produto fora de estoque.'})
        messages.error(request, f'{product.name} está fora de estoque.')
        return redirect('catalog:product_detail', slug=product.slug)

    quantity = max(1, int(request.POST.get('quantity', 1)))
    cart = _get_or_create_cart(request)

    item, created = CartItem.objects.get_or_create(
        cart=cart, product=product,
        defaults={'quantity': quantity},
    )
    if not created:
        item.quantity = F('quantity') + quantity
        item.save(update_fields=['quantity'])

    # Conta fresco do banco
    count = _cart_count(cart)

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        # AJAX: apenas JSON — NÃO chama messages.success (evita ghost message)
        return JsonResponse({
            'success': True,
            'cart_count': count,
            'product_name': product.name,
        })

    messages.success(request, f'{product.name} adicionado ao carrinho!')
    return redirect('orders:cart')


@require_POST
def remove_from_cart(request, item_id):
    cart = _get_or_create_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    item.delete()
    messages.success(request, 'Item removido do carrinho.')
    return redirect('orders:cart')


@require_POST
def update_cart(request, item_id):
    cart = _get_or_create_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        item.quantity = quantity
        item.save(update_fields=['quantity'])
    else:
        item.delete()
    return redirect('orders:cart')


# ── Checkout ──────────────────────────────────────────────────────

PAYMENT_METHODS = [
    ('credit_card', 'Cartão de Crédito', 'fa-credit-card'),
    ('debit_card',  'Cartão de Débito',  'fa-credit-card'),
    ('pix',         'PIX',               'fa-qrcode'),
    ('cash',        'Dinheiro',          'fa-money-bill-wave'),
]


@login_required
def checkout_view(request):
    cart = _get_or_create_cart(request)
    if not cart.items.exists():
        messages.warning(request, 'Seu carrinho está vazio.')
        return redirect('orders:cart')

    from apps.accounts.models import Address
    addresses = Address.objects.filter(user=request.user)

    if request.method == 'POST':
        delivery_type  = request.POST.get('delivery_type', 'pickup')
        payment_method = request.POST.get('payment_method', 'pix')
        address_id     = request.POST.get('address_id')
        notes          = request.POST.get('notes', '').strip()

        address = None
        if delivery_type == 'delivery' and address_id:
            try:
                address = Address.objects.get(pk=address_id, user=request.user)
            except Address.DoesNotExist:
                pass

        subtotal     = cart.total
        delivery_fee = 10 if delivery_type == 'delivery' else 0
        total        = subtotal + delivery_fee

        order = Order.objects.create(
            user=request.user,
            delivery_type=delivery_type,
            payment_method=payment_method,
            address=address,
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            total=total,
            notes=notes,
        )

        for item in cart.items.select_related('product__stock').all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.product.current_price,
            )
            # Baixa estoque
            try:
                item.product.stock.quantity = F('quantity') - item.quantity
                item.product.stock.save(update_fields=['quantity'])
            except Exception:
                pass

        cart.items.all().delete()
        messages.success(
            request,
            f'Pedido #{order.order_number} realizado com sucesso! 🎉'
        )
        return redirect('orders:order_detail', order_number=order.order_number)

    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'addresses': addresses,
        'payment_methods': PAYMENT_METHODS,
        'has_addresses': addresses.exists(),
    })


# ── Orders ────────────────────────────────────────────────────────

@login_required
def order_list(request):
    orders = request.user.orders.all().order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    DELIVERY_STAGES = [
        {'key': 'pending',   'label': 'Pedido',     'icon': 'fa-clock'},
        {'key': 'confirmed', 'label': 'Confirmado', 'icon': 'fa-check'},
        {'key': 'preparing', 'label': 'Preparando', 'icon': 'fa-box'},
        {'key': 'shipped',   'label': 'Em entrega', 'icon': 'fa-motorcycle'},
        {'key': 'delivered', 'label': 'Entregue',   'icon': 'fa-home'},
    ]
    PICKUP_STAGES = [
        {'key': 'pending',   'label': 'Pedido',    'icon': 'fa-clock'},
        {'key': 'confirmed', 'label': 'Confirmado','icon': 'fa-check'},
        {'key': 'preparing', 'label': 'Preparando','icon': 'fa-box'},
        {'key': 'ready',     'label': 'Pronto',    'icon': 'fa-bell'},
        {'key': 'delivered', 'label': 'Retirado',  'icon': 'fa-store'},
    ]

    if order.status == 'cancelled':
        stages = [{'key': 'cancelled', 'label': 'Cancelado',
                   'icon': 'fa-times', 'done': False, 'active': True}]
        progress_pct = 0
    else:
        stages = PICKUP_STAGES if order.delivery_type == 'pickup' else DELIVERY_STAGES
        keys = [s['key'] for s in stages]
        current_idx = keys.index(order.status) if order.status in keys else 0
        for i, stage in enumerate(stages):
            stage['done']   = i < current_idx
            stage['active'] = i == current_idx
        progress_pct = int((current_idx / max(len(stages) - 1, 1)) * 100)

    return render(request, 'orders/order_detail.html', {
        'order': order,
        'stages': stages,
        'progress_pct': progress_pct,
    })

@login_required
def order_detail_by_pk(request, pk):
    """Compatibilidade: redireciona links antigos /pedido/<pk>/ para /pedido/<order_number>/"""
    from django.shortcuts import redirect
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return redirect('orders:order_detail', order_number=order.order_number, permanent=True)