from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.http import JsonResponse
from .models import UserProfile, Address, Wishlist, WishlistItem
from .forms import RegistrationForm, LoginForm, UserProfileForm, AddressForm
from products.models import Product
from cart.models import Cart, CartItem


def register_view(request):
    if request.user.is_authenticated:
        return redirect('customer_profile')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Update UserProfile phone
            phone = form.cleaned_data.get('phone')
            if phone and hasattr(user, 'profile'):
                user.profile.phone = phone
                user.profile.save()

            # Ensure wishlist created
            Wishlist.objects.get_or_create(user=user)

            # Auto-login after registration
            login(request, user)
            messages.success(request, f"Welcome to Aura Jewellery, {user.first_name}! Your royal account is ready.")
            return redirect('customer_profile')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('customer_profile')

    next_url = request.GET.get('next', 'customer_profile')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Check if user entered email
            user_obj = None
            if '@' in username_or_email:
                user_match = User.objects.filter(email=username_or_email).first()
                if user_match:
                    user_obj = authenticate(request, username=user_match.username, password=password)
            else:
                user_obj = authenticate(request, username=username_or_email, password=password)

            if user_obj is not None:
                login(request, user_obj)
                
                # Merge session cart into user cart if any
                session_key = request.session.session_key
                if session_key:
                    guest_cart = Cart.objects.filter(session_key=session_key).first()
                    if guest_cart and guest_cart.items.exists():
                        user_cart, _ = Cart.objects.get_or_create(user=user_obj)
                        for item in guest_cart.items.all():
                            c_item, created = CartItem.objects.get_or_create(cart=user_cart, product=item.product)
                            if not created:
                                c_item.quantity += item.quantity
                            else:
                                c_item.quantity = item.quantity
                            c_item.save()
                        guest_cart.delete()

                messages.success(request, f"Welcome back, {user_obj.first_name or user_obj.username}!")
                return redirect(next_url if next_url else 'customer_profile')
            else:
                messages.error(request, "Invalid username/email or password. Please try again.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')


@login_required
def profile_view(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        if form.is_valid():
            form.save()
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            messages.success(request, "Your profile details have been updated.")
            return redirect('customer_profile')
    else:
        initial = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
        form = UserProfileForm(instance=profile, initial=initial)

    recent_orders = user.orders.all()[:5]
    custom_orders = user.custom_orders.all()[:3]
    default_address = user.addresses.filter(is_default=True).first()

    context = {
        'form': form,
        'profile': profile,
        'recent_orders': recent_orders,
        'custom_orders': custom_orders,
        'default_address': default_address,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was changed successfully.")
            return redirect('customer_profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def address_list_view(request):
    addresses = request.user.addresses.all()
    return render(request, 'accounts/addresses.html', {'addresses': addresses})


@login_required
def address_create_view(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            if not request.user.addresses.exists():
                address.is_default = True
            address.save()
            messages.success(request, "New address added successfully.")
            return redirect('address_list')
    else:
        form = AddressForm()

    return render(request, 'accounts/address_form.html', {'form': form, 'title': 'Add New Address'})


@login_required
def address_edit_view(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "Address updated successfully.")
            return redirect('address_list')
    else:
        form = AddressForm(instance=address)

    return render(request, 'accounts/address_form.html', {'form': form, 'title': 'Edit Address'})


@login_required
def address_delete_view(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    if request.method == 'POST':
        address.delete()
        messages.success(request, "Address removed.")
        return redirect('address_list')
    return render(request, 'accounts/address_confirm_delete.html', {'address': address})


@login_required
def wishlist_view(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    items = wishlist.items.select_related('product', 'product__category').all()
    return render(request, 'accounts/wishlist.html', {'wishlist_items': items})


@login_required
def wishlist_toggle_api(request, product_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    product = get_object_or_404(Product, id=product_id)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    
    item = WishlistItem.objects.filter(wishlist=wishlist, product=product).first()
    if item:
        item.delete()
        status_str = 'removed'
        msg = f"Removed '{product.name}' from your Wishlist."
    else:
        WishlistItem.objects.create(wishlist=wishlist, product=product)
        status_str = 'added'
        msg = f"Added '{product.name}' to your Wishlist."

    total_count = wishlist.items.count()
    return JsonResponse({
        'status': status_str,
        'message': msg,
        'wishlist_count': total_count
    })


@login_required
def wishlist_move_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist = Wishlist.objects.filter(user=request.user).first()
    if wishlist:
        WishlistItem.objects.filter(wishlist=wishlist, product=product).delete()

    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += 1
        item.save()

    messages.success(request, f"Moved '{product.name}' to your Shopping Bag!")
    return redirect('cart_detail')


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            messages.success(request, "If an account exists with this email, password reset instructions have been dispatched to your inbox.")
        else:
            messages.info(request, "If an account exists with this email, password reset instructions have been dispatched to your inbox.")
        return redirect('login')
    return render(request, 'accounts/password_reset.html')
