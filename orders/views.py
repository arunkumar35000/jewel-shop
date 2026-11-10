import uuid
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Order, OrderItem, Payment
from cart.models import Cart
from accounts.models import Address


def checkout_view(request):
    """
    Complete luxury checkout flow with shipping address selection,
    payment method selection, and order placement.
    """
    # Get current user or guest cart
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        saved_addresses = request.user.addresses.all()
    else:
        session_key = request.session.session_key
        cart = Cart.objects.filter(session_key=session_key).first() if session_key else None
        saved_addresses = []

    if not cart or not cart.items.exists():
        messages.warning(request, "Your shopping bag is empty. Please add items before checking out.")
        return redirect('product_list')

    if request.method == 'POST':
        # Customer contact info
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()

        # Shipping Address Resolution
        selected_address_id = request.POST.get('selected_address_id')
        if selected_address_id and request.user.is_authenticated:
            addr = get_object_or_404(Address, id=selected_address_id, user=request.user)
            shipping_addr_text = addr.single_line_address
            if not full_name: full_name = addr.full_name
            if not phone: phone = addr.phone
        else:
            street = request.POST.get('street_address', '').strip()
            city = request.POST.get('city', '').strip()
            state = request.POST.get('state', '').strip()
            pincode = request.POST.get('pincode', '').strip()
            shipping_addr_text = f"{street}, {city}, {state} - {pincode}, India"

            # Optionally save address for user
            if request.user.is_authenticated and request.POST.get('save_address') == '1':
                Address.objects.create(
                    user=request.user,
                    address_type='SHIPPING',
                    full_name=full_name,
                    phone=phone,
                    street_address=street,
                    city=city,
                    state=state,
                    pincode=pincode,
                    is_default=(request.user.addresses.count() == 0)
                )

        # Billing address
        billing_same = request.POST.get('billing_same') == '1'
        if billing_same:
            billing_addr_text = shipping_addr_text
        else:
            b_street = request.POST.get('billing_street', shipping_addr_text)
            billing_addr_text = b_street

        payment_method = request.POST.get('payment_method', 'UPI')
        order_notes = request.POST.get('order_notes', '')

        # Create Order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            customer_name=full_name,
            customer_email=email or (request.user.email if request.user.is_authenticated else ''),
            customer_phone=phone,
            shipping_address=shipping_addr_text,
            billing_address=billing_addr_text,
            items_total=cart.subtotal,
            making_charges_total=cart.total_making_charges,
            tax_amount=cart.gst_amount,
            grand_total=cart.grand_total,
            payment_method=payment_method,
            payment_status='PAID' if payment_method in ['UPI', 'ONLINE_CARD'] else 'PENDING',
            order_status='CONFIRMED' if payment_method in ['UPI', 'ONLINE_CARD'] else 'PENDING',
            order_notes=order_notes,
            estimated_delivery=timezone.now().date() + timezone.timedelta(days=4)
        )

        # Snapshot order items
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                product_sku=item.product.sku,
                metal_type=item.product.metal_type,
                purity=item.product.purity,
                gross_weight=item.product.gross_weight,
                net_weight=item.product.net_weight,
                stone_weight=item.product.stone_weight,
                unit_price=item.product.final_price,
                making_charges=item.product.making_charges,
                quantity=item.quantity,
                total_price=item.item_subtotal,
            )
            # Reduce inventory
            if item.product.stock >= item.quantity:
                item.product.stock -= item.quantity
                item.product.save()

        # Create Payment Record
        txn_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"
        Payment.objects.create(
            order=order,
            transaction_id=txn_id,
            payment_method=order.get_payment_method_display(),
            amount=order.grand_total,
            status='SUCCESS' if order.payment_status == 'PAID' else 'PENDING',
            payment_details=f"Payment via {order.get_payment_method_display()} (Txn Ref: {txn_id})"
        )

        # Clear cart
        cart.items.all().delete()

        messages.success(request, f"Order #{order.order_number} confirmed! Thank you for trusting Aura Jewellery.")
        return redirect('order_confirmation', order_number=order.order_number)

    context = {
        'cart': cart,
        'saved_addresses': saved_addresses,
    }
    return render(request, 'orders/checkout.html', context)


def order_confirmation_view(request, order_number):
    order = get_object_or_404(Order.objects.prefetch_related('items'), order_number=order_number)
    return render(request, 'orders/order_confirmation.html', {'order': order})


@login_required
def order_history_view(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    return render(request, 'orders/order_history.html', {'orders': orders})


def order_detail_view(request, order_number):
    if request.user.is_authenticated:
        order = get_object_or_404(Order.objects.prefetch_related('items', 'payments'), order_number=order_number)
    else:
        order = get_object_or_404(Order.objects.prefetch_related('items', 'payments'), order_number=order_number)

    return render(request, 'orders/order_detail.html', {'order': order})


def order_tracking_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'orders/order_tracking.html', {'order': order})


def invoice_view(request, order_number):
    """
    Printable / Downloadable GST-compliant Tax Invoice
    with HSN Code 7113, CGST 1.5%, SGST 1.5%, and company credentials.
    """
    order = get_object_or_404(Order.objects.prefetch_related('items'), order_number=order_number)
    
    # Split GST into CGST (1.5%) and SGST (1.5%) for GST invoice compliance
    cgst_amount = round(order.tax_amount / Decimal('2.0'), 2)
    sgst_amount = round(order.tax_amount - cgst_amount, 2)

    return render(request, 'orders/invoice.html', {
        'order': order,
        'cgst_amount': cgst_amount,
        'sgst_amount': sgst_amount,
    })


@login_required
def order_cancel_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    if order.can_cancel:
        order.order_status = 'CANCELLED'
        order.save()
        
        # Restore stock
        for item in order.items.all():
            if item.product:
                item.product.stock += item.quantity
                item.product.save()

        messages.info(request, f"Order #{order.order_number} has been cancelled.")
    else:
        messages.error(request, "This order cannot be cancelled as it is already in crafting or dispatched.")

    return redirect('order_detail', order_number=order.order_number)
