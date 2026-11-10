from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from products.models import Product
from .models import Cart, CartItem


def _get_or_create_cart(request):
    """
    Retrieves or creates a shopping cart for the current user or guest session.
    """
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.save()
        session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key)
    return cart


def cart_detail(request):
    cart = _get_or_create_cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})


def cart_add(request):
    if request.method == 'POST':
        is_ajax_request = (
            request.is_ajax()
            or request.headers.get('x-requested-with') == 'XMLHttpRequest'
            or request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
            or 'application/json' in request.META.get('HTTP_ACCEPT', '')
            or request.POST.get('ajax') == '1'
            or request.POST.get('format') == 'json'
        )

        product_id = request.POST.get('product_id')
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1

        if not product_id and request.body:
            import json
            try:
                data = json.loads(request.body.decode('utf-8'))
                product_id = data.get('product_id')
                quantity = int(data.get('quantity', 1))
            except Exception:
                pass

        if not product_id:
            if is_ajax_request:
                return JsonResponse({'success': False, 'error': 'Product ID is missing.'}, status=400)
            messages.error(request, "Product not found.")
            return redirect('product_list')

        product = get_object_or_404(Product, id=product_id, status='ACTIVE')
        cart = _get_or_create_cart(request)

        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = max(1, quantity)
        item.save()

        if is_ajax_request:
            return JsonResponse({
                'success': True,
                'message': f"Added '{product.name}' to your Shopping Bag!",
                'total_items': cart.total_items,
                'subtotal': str(cart.subtotal),
                'grand_total': str(cart.grand_total),
            })

        messages.success(request, f"Added '{product.name}' to your Shopping Bag!")
        return redirect('cart_detail')

    return redirect('product_list')


def cart_update(request, item_id):
    if request.method == 'POST':
        cart = _get_or_create_cart(request)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        action = request.POST.get('action')

        if action == 'increase':
            item.quantity += 1
            item.save()
        elif action == 'decrease':
            if item.quantity > 1:
                item.quantity -= 1
                item.save()
            else:
                item.delete()
        elif action == 'set':
            try:
                qty = int(request.POST.get('quantity', 1))
                if qty > 0:
                    item.quantity = qty
                    item.save()
                else:
                    item.delete()
            except ValueError:
                pass

        messages.success(request, "Shopping bag updated.")
    return redirect('cart_detail')


def cart_remove(request, item_id):
    cart = _get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    name = item.product.name
    item.delete()
    messages.info(request, f"Removed '{name}' from your Shopping Bag.")
    return redirect('cart_detail')


def cart_quick_view(request):
    """
    Returns snippet HTML for the offcanvas drawer.
    """
    cart = _get_or_create_cart(request)
    return render(request, 'cart/includes/drawer_snippet.html', {'cart_instance': cart})
