from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator
from products.models import Product, Category
from orders.models import Order, OrderItem, Payment
from custom_orders.models import CustomOrder, CustomOrderQuotation
from custom_orders.forms import QuotationForm


def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@user_passes_test(is_admin)
def admin_dashboard(request):
    """
    Luxury Executive Admin Dashboard with KPI analytics,
    recent orders, customization requests, and sales summary.
    """
    total_products = Product.objects.count()
    total_customers = User.objects.filter(is_staff=False).count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(order_status__in=['PENDING', 'CONFIRMED']).count()
    total_custom_requests = CustomOrder.objects.count()
    pending_custom_requests = CustomOrder.objects.filter(status__in=['PENDING', 'UNDER_REVIEW']).count()

    # Total Sales Revenue
    sales_agg = Order.objects.filter(payment_status='PAID').aggregate(Sum('grand_total'))
    total_sales = sales_agg['grand_total__sum'] or Decimal('0.00')

    # Transactions & Stripe Metrics
    recent_transactions = Payment.objects.select_related('order').all().order_by('-created_at')[:8]
    total_transactions = Payment.objects.count()
    successful_transactions = Payment.objects.filter(status='SUCCESS').count()
    stripe_transactions_count = Payment.objects.filter(payment_method__icontains='Stripe').count()

    # Category product distribution for Chart.js
    category_counts = Category.objects.annotate(prod_count=Count('products')).values('name', 'prod_count')
    cat_labels = [c['name'] for c in category_counts]
    cat_data = [c['prod_count'] for c in category_counts]

    # Recent Orders & Custom Requests
    recent_orders = Order.objects.all().order_by('-created_at')[:6]
    recent_custom_requests = CustomOrder.objects.all().order_by('-created_at')[:6]

    context = {
        'total_products': total_products,
        'total_customers': total_customers,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_custom_requests': total_custom_requests,
        'pending_custom_requests': pending_custom_requests,
        'total_sales': total_sales,
        'recent_transactions': recent_transactions,
        'total_transactions': total_transactions,
        'successful_transactions': successful_transactions,
        'stripe_transactions_count': stripe_transactions_count,
        'recent_orders': recent_orders,
        'recent_custom_requests': recent_custom_requests,
        'cat_labels': cat_labels,
        'cat_data': cat_data,
    }
    return render(request, 'admin_panel/dashboard.html', context)


@user_passes_test(is_admin)
def admin_transactions_list(request):
    """
    Dedicated view for full payment transactions ledger
    displaying Stripe, UPI, and card payments.
    """
    transactions = Payment.objects.select_related('order').all().order_by('-created_at')

    status_filter = request.GET.get('status')
    if status_filter:
        transactions = transactions.filter(status=status_filter)

    method_filter = request.GET.get('method')
    if method_filter:
        transactions = transactions.filter(payment_method__icontains=method_filter)

    q = request.GET.get('q', '').strip()
    if q:
        transactions = transactions.filter(
            Q(transaction_id__icontains=q) |
            Q(order__order_number__icontains=q) |
            Q(order__customer_name__icontains=q) |
            Q(order__customer_email__icontains=q)
        )

    paginator = Paginator(transactions, 15)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    return render(request, 'admin_panel/transactions_list.html', {
        'transactions': page_obj,
        'status_filter': status_filter,
        'method_filter': method_filter,
        'q': q,
        'total_count': transactions.count(),
        'successful_count': Payment.objects.filter(status='SUCCESS').count(),
    })


@user_passes_test(is_admin)
def admin_orders_list(request):
    orders = Order.objects.all().order_by('-created_at')

    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(order_status=status_filter)

    q = request.GET.get('q', '').strip()
    if q:
        orders = orders.filter(
            Q(order_number__icontains=q) |
            Q(customer_name__icontains=q) |
            Q(customer_phone__icontains=q)
        )

    paginator = Paginator(orders, 15)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    return render(request, 'admin_panel/orders_list.html', {
        'orders': page_obj,
        'status_filter': status_filter,
        'q': q,
        'status_choices': Order.ORDER_STATUS_CHOICES,
    })


@user_passes_test(is_admin)
def admin_order_detail(request, order_number):
    order = get_object_or_404(Order.objects.prefetch_related('items', 'payments'), order_number=order_number)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_status':
            new_status = request.POST.get('order_status')
            new_payment = request.POST.get('payment_status')
            tracking_num = request.POST.get('tracking_number', '')
            courier = request.POST.get('courier_partner', '')

            if new_status: order.order_status = new_status
            if new_payment: order.payment_status = new_payment
            if tracking_num: order.tracking_number = tracking_num
            if courier: order.courier_partner = courier

            order.save()
            messages.success(request, f"Order #{order.order_number} status updated successfully.")
            return redirect('admin_order_detail', order_number=order.order_number)

    return render(request, 'admin_panel/order_detail.html', {'order': order})


@user_passes_test(is_admin)
def admin_custom_requests_list(request):
    requests_qs = CustomOrder.objects.all().order_by('-created_at')

    status = request.GET.get('status')
    if status:
        requests_qs = requests_qs.filter(status=status)

    q = request.GET.get('q', '').strip()
    if q:
        requests_qs = requests_qs.filter(
            Q(request_id__icontains=q) |
            Q(full_name__icontains=q) |
            Q(email__icontains=q) |
            Q(phone__icontains=q)
        )

    paginator = Paginator(requests_qs, 15)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    return render(request, 'admin_panel/custom_requests_list.html', {
        'requests': page_obj,
        'selected_status': status,
        'q': q,
        'status_choices': CustomOrder.STATUS_CHOICES,
    })


@user_passes_test(is_admin)
def admin_custom_request_detail(request, request_id):
    custom_order = get_object_or_404(
        CustomOrder.objects.prefetch_related('reference_images', 'quotations'),
        request_id=request_id
    )

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_status':
            new_status = request.POST.get('status')
            notes = request.POST.get('admin_notes', '')
            if new_status: custom_order.status = new_status
            custom_order.admin_notes = notes
            custom_order.save()
            messages.success(request, f"Request #{custom_order.request_id} updated.")
            return redirect('admin_custom_request_detail', request_id=custom_order.request_id)

    return render(request, 'admin_panel/custom_request_detail.html', {
        'order': custom_order,
        'images': custom_order.reference_images.all(),
        'quotations': custom_order.quotations.all(),
    })


@user_passes_test(is_admin)
def admin_quotation_create(request, request_id):
    custom_order = get_object_or_404(CustomOrder, request_id=request_id)

    if request.method == 'POST':
        form = QuotationForm(request.POST, request.FILES)
        if form.is_valid():
            quote = form.save(commit=False)
            quote.custom_order = custom_order
            quote.save()

            # Advance status to QUOTATION_SENT
            custom_order.status = 'QUOTATION_SENT'
            custom_order.save()

            messages.success(request, f"Quotation #{quote.quotation_number} sent to customer {custom_order.full_name}!")
            return redirect('admin_custom_request_detail', request_id=custom_order.request_id)
    else:
        # Prepopulate with defaults from request
        initial = {
            'estimated_weight': custom_order.expected_weight,
            'metal_rate_applied': Decimal('6830.00') if custom_order.gold_purity == '22K' else Decimal('7450.00'),
            'making_charges': Decimal('12000.00'),
            'estimated_making_days': 15,
        }
        form = QuotationForm(initial=initial)

    return render(request, 'admin_panel/quotation_form.html', {
        'form': form,
        'order': custom_order
    })


@user_passes_test(is_admin)
def admin_customers_list(request):
    customers = User.objects.filter(is_staff=False).annotate(
        orders_count=Count('orders'),
        total_spent=Sum('orders__grand_total')
    ).order_by('-date_joined')

    q = request.GET.get('q', '').strip()
    if q:
        customers = customers.filter(
            Q(username__icontains=q) |
            Q(email__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q)
        )

    paginator = Paginator(customers, 15)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    return render(request, 'admin_panel/customers_list.html', {'customers': page_obj, 'q': q})


@user_passes_test(is_admin)
def admin_customer_detail(request, customer_id):
    customer = get_object_or_404(User, id=customer_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'toggle_status':
            customer.is_active = not customer.is_active
            customer.save()
            messages.success(request, f"Customer account status toggled to {'Active' if customer.is_active else 'Disabled'}.")
            return redirect('admin_customer_detail', customer_id=customer.id)

    orders = customer.orders.all().order_by('-created_at')
    custom_requests = customer.custom_orders.all().order_by('-created_at')
    addresses = customer.addresses.all()

    return render(request, 'admin_panel/customer_detail.html', {
        'customer': customer,
        'orders': orders,
        'custom_requests': custom_requests,
        'addresses': addresses,
    })
