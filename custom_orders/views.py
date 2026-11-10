from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomOrder, CustomOrderImage, CustomOrderQuotation
from .forms import CustomOrderRequestForm, QuotationForm


def custom_order_create(request):
    """
    Dedicated Custom Jewellery Design Request Form
    with multi-file reference image uploads.
    """
    if request.method == 'POST':
        form = CustomOrderRequestForm(request.POST)
        if form.is_valid():
            custom_order = form.save(commit=False)
            if request.user.is_authenticated:
                custom_order.user = request.user
            custom_order.save()

            # Handle multiple reference images upload
            files = request.FILES.getlist('reference_images')
            valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
            uploaded_count = 0

            for f in files:
                ext = f.name.lower().split('.')[-1]
                if f".{ext}" in valid_extensions:
                    CustomOrderImage.objects.create(
                        custom_order=custom_order,
                        image=f,
                        caption=f.name
                    )
                    uploaded_count += 1

            messages.success(
                request,
                f"Your custom jewellery request #{custom_order.request_id} has been submitted with {uploaded_count} reference image(s). Our master artisans are reviewing it."
            )
            return redirect('custom_order_success', request_id=custom_order.request_id)
        else:
            messages.error(request, "Please review the form for errors.")
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'full_name': request.user.get_full_name(),
                'email': request.user.email,
                'phone': getattr(request.user.profile, 'phone', ''),
            }
        form = CustomOrderRequestForm(initial=initial)

    return render(request, 'custom_orders/custom_request_form.html', {'form': form})


def custom_order_success(request, request_id):
    custom_order = get_object_or_404(CustomOrder, request_id=request_id)
    return render(request, 'custom_orders/custom_request_success.html', {'order': custom_order})


@login_required
def customer_custom_orders(request):
    orders = CustomOrder.objects.filter(user=request.user).prefetch_related('reference_images', 'quotations')
    return render(request, 'custom_orders/custom_order_list.html', {'custom_orders': orders})


def customer_custom_order_detail(request, request_id):
    custom_order = get_object_or_404(
        CustomOrder.objects.prefetch_related('reference_images', 'quotations'),
        request_id=request_id
    )
    latest_quote = custom_order.quotations.last()

    return render(request, 'custom_orders/custom_order_detail.html', {
        'order': custom_order,
        'latest_quote': latest_quote,
        'images': custom_order.reference_images.all(),
    })


@login_required
def quotation_respond(request, request_id):
    """
    Allows customer to Accept or Request Revision for an artisan quotation.
    """
    custom_order = get_object_or_404(CustomOrder, request_id=request_id, user=request.user)
    latest_quote = custom_order.quotations.last()

    if request.method == 'POST' and latest_quote:
        action = request.POST.get('action')
        feedback = request.POST.get('feedback', '')

        if action == 'accept':
            latest_quote.status = 'ACCEPTED'
            latest_quote.customer_feedback = feedback
            latest_quote.save()

            custom_order.status = 'APPROVED'
            custom_order.save()
            messages.success(request, "Quotation Accepted! Handcrafting and hallmarking will commence immediately.")

        elif action == 'revision':
            latest_quote.status = 'REVISION_REQUESTED'
            latest_quote.customer_feedback = feedback
            latest_quote.save()

            custom_order.status = 'DESIGN_PREPARATION'
            custom_order.save()
            messages.info(request, "Revision request submitted. Our artisan will update the 3D CAD design.")

        return redirect('customer_custom_order_detail', request_id=custom_order.request_id)

    return redirect('customer_custom_orders')
