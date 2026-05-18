from django.db.models import Sum


def cart_processor(request):
    from apps.orders.models import Cart

    cart       = None
    cart_count = 0

    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            key = request.session.session_key
            if key:
                cart = Cart.objects.filter(
                    session_key=key,
                    user__isnull=True,
                ).first()

        if cart:
            cart_count = (
                cart.items.aggregate(total=Sum('quantity'))['total'] or 0
            )
    except Exception:
        pass

    return {'cart': cart, 'cart_count': cart_count}