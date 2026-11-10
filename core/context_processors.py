from django.conf import settings


def jewellery_context(request):
    """
    Global context processor injecting gold rates, categories,
    cart item count, and wishlist count across all templates.
    """
    context = {
        'DAILY_GOLD_RATES': getattr(settings, 'DAILY_GOLD_RATES', {}),
        'JEWELLERY_GST_PERCENT': getattr(settings, 'JEWELLERY_GST_PERCENT', 3.0),
        'cart_count': 0,
        'wishlist_count': 0,
        'navbar_categories': [],
    }

    # Fetch navbar categories
    try:
        from products.models import Category
        context['navbar_categories'] = Category.objects.filter(is_active=True).prefetch_related('subcategories')[:8]
    except Exception:
        context['navbar_categories'] = []

    # Calculate cart count
    try:
        from cart.models import Cart
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.save()
                session_key = request.session.session_key
            cart = Cart.objects.filter(session_key=session_key).first()

        if cart:
            context['cart_count'] = cart.total_items
            context['cart_instance'] = cart
    except Exception:
        context['cart_count'] = 0

    # Calculate wishlist count
    try:
        from accounts.models import Wishlist
        if request.user.is_authenticated:
            wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
            context['wishlist_count'] = wishlist.items.count()
    except Exception:
        context['wishlist_count'] = 0

    return context

