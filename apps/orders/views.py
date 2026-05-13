from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Cart, CartItem, Order, OrderItem
from apps.catalog.models import Product


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(
            session_key=request.session.session_key
        )
    return cart


def cart_view(request):
    cart = get_or_create_cart(request)
    return render(request, 'orders/cart.html', {'cart': cart})


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = get_or_create_cart(request)
    quantity = int(request.POST.get('quantity', 1))

    stock = getattr(product, 'stock', None)
    if stock and stock.available_quantity < quantity:
        messages.error(request, 'Quantidade indisponível em estoque.')
        return redirect('catalog:product_detail', slug=product.slug)

    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += quantity
    else:
        item.quantity = quantity
    item.save()

    messages.success(request, f'{product.name} adicionado ao carrinho!')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_count': cart.total_items})
    return redirect('orders:cart')


@require_POST
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id)
    cart = get_or_create_cart(request)
    if item.cart == cart:
        item.delete()
        messages.success(request, 'Item removido do carrinho.')
    return redirect('orders:cart')


@require_POST
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id)
    cart = get_or_create_cart(request)
    quantity = int(request.POST.get('quantity', 1))
    if item.cart == cart:
        if quantity > 0:
            item.quantity = quantity
            item.save()
        else:
            item.delete()
    return redirect('orders:cart')


PAYMENT_METHODS = [
    ('credit_card', 'Crédito', 'fa-credit-card'),
    ('debit_card', 'Débito', 'fa-credit-card'),
    ('pix', 'PIX', 'fa-qrcode'),
    ('cash', 'Dinheiro', 'fa-money-bill-wave'),
]


@login_required
def checkout_view(request):
    cart = get_or_create_cart(request)
    if not cart.items.exists():
        messages.warning(request, 'Seu carrinho está vazio.')
        return redirect('orders:cart')

    addresses = request.user.addresses.all()

    if request.method == 'POST':
        delivery_type = request.POST.get('delivery_type')
        payment_method = request.POST.get('payment_method')
        address_id = request.POST.get('address_id')
        notes = request.POST.get('notes', '')

        address = None
        if delivery_type == 'delivery' and address_id:
            address = get_object_or_404(
                request.user.addresses, pk=address_id
            )

        subtotal = cart.total
        delivery_fee = 10 if delivery_type == 'delivery' else 0
        total = subtotal + delivery_fee

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

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.product.current_price,
            )
            if hasattr(item.product, 'stock'):
                item.product.stock.quantity -= item.quantity
                item.product.stock.save()

        cart.items.all().delete()
        messages.success(
            request,
            f'Pedido #{order.order_number} realizado com sucesso!'
        )
        return redirect('orders:order_detail', pk=order.pk)

    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'addresses': addresses,
        'payment_methods': PAYMENT_METHODS,
    })


@login_required
def order_list_view(request):
    orders = request.user.orders.all().order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail_view(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    steps = [
        ('pending',   'Pendente'),
        ('confirmed', 'Confirmado'),
        ('preparing', 'Em preparo'),
        ('ready',     'Pronto'),
        ('delivered', 'Entregue'),
    ]
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'steps': steps,
    })