import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings
from .models import Product, ProductImage, Product360Image, Category, SubCategory, Review
from .forms import ProductForm, ProductImageForm, CategoryForm, ReviewForm
from accounts.models import Wishlist


def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def product_list(request, category_slug=None):
    """
    Customer product catalog with multi-facet filters, search, and sorting.
    """
    products = Product.objects.filter(status='ACTIVE').select_related('category', 'subcategory').prefetch_related('images', 'images_360')
    current_category = None

    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = products.filter(category=current_category)

    # Search filter
    q = request.GET.get('q', '').strip()
    if q:
        products = products.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(sku__icontains=q) |
            Q(category__name__icontains=q)
        )

    # Facet Filters
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    metal_type = request.GET.get('metal')
    if metal_type:
        products = products.filter(metal_type=metal_type)

    purity = request.GET.get('purity')
    if purity:
        products = products.filter(purity=purity)

    gender = request.GET.get('gender')
    if gender:
        products = products.filter(gender=gender)

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(base_price__gte=Decimal(min_price))
    if max_price:
        products = products.filter(base_price__lte=Decimal(max_price))

    has_360 = request.GET.get('has_360')
    if has_360 == '1':
        products = products.filter(images_360__isnull=False).distinct()

    # Sorting
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_asc':
        products = products.order_by('base_price')
    elif sort == 'price_desc':
        products = products.order_by('-base_price')
    elif sort == 'bestseller':
        products = products.order_by('-is_bestseller', '-created_at')
    elif sort == 'discount':
        products = products.order_by('-discount_percent', '-created_at')
    else: # newest
        products = products.order_by('-created_at')

    # Wishlist IDs for authenticated user
    user_wishlist_ids = set()
    if request.user.is_authenticated:
        user_wishlist_ids = set(request.user.wishlist.items.values_list('product_id', flat=True)) if hasattr(request.user, 'wishlist') else set()

    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    all_categories = Category.objects.filter(is_active=True).order_by('display_order')

    context = {
        'products': page_obj,
        'current_category': current_category,
        'all_categories': all_categories,
        'user_wishlist_ids': user_wishlist_ids,
        'total_count': paginator.count,
        'sort': sort,
        'q': q,
        'selected_metal': metal_type,
        'selected_purity': purity,
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, slug):
    """
    Advanced jewellery product details page with 360-degree multi-frame viewer,
    PhotoSwipe image zoom, gold calculation breakdown, reviews, and related products.
    """
    product = get_object_or_404(
        Product.objects.select_related('category', 'subcategory').prefetch_related('images', 'images_360', 'reviews__user'),
        slug=slug
    )

    # 360-degree image frames sequence as JSON list of URLs
    frames_360 = [img.image.url for img in product.images_360.all().order_by('frame_number')]
    frames_360_json = json.dumps(frames_360)

    # Review submission handling
    review_form = ReviewForm()
    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.is_verified_purchase = True
            review.save()
            messages.success(request, "Thank you! Your review has been published.")
            return redirect('product_detail', slug=product.slug)

    # Calculate gold breakdown transparency
    daily_rates = getattr(settings, 'DAILY_GOLD_RATES', {})
    purity_rate = daily_rates.get(product.purity, daily_rates.get('22K', Decimal('6830.00')))
    calculated_gold_value = round(product.net_weight * purity_rate, 2)
    gst_percent = getattr(settings, 'JEWELLERY_GST_PERCENT', Decimal('3.00'))
    estimated_gst = round((product.final_price * gst_percent) / Decimal('100.00'), 2)
    grand_total_estimate = round(product.final_price + estimated_gst, 2)

    # Related products
    related_products = Product.objects.filter(
        category=product.category, status='ACTIVE'
    ).exclude(id=product.id).prefetch_related('images')[:4]

    # Wishlist status
    in_wishlist = False
    if request.user.is_authenticated and hasattr(request.user, 'wishlist'):
        in_wishlist = request.user.wishlist.items.filter(product=product).exists()

    context = {
        'product': product,
        'gallery_images': product.images.all(),
        'frames_360': frames_360,
        'frames_360_json': frames_360_json,
        'calculated_gold_value': calculated_gold_value,
        'purity_rate': purity_rate,
        'estimated_gst': estimated_gst,
        'grand_total_estimate': grand_total_estimate,
        'related_products': related_products,
        'review_form': review_form,
        'reviews': product.reviews.filter(is_approved=True),
        'in_wishlist': in_wishlist,
    }
    return render(request, 'products/product_detail.html', context)


# ==============================================================================
# ADMIN PRODUCT MANAGEMENT (CRUD)
# ==============================================================================

@user_passes_test(is_admin)
def admin_product_list(request):
    products = Product.objects.all().select_related('category', 'subcategory').order_by('-created_at')
    
    q = request.GET.get('q', '').strip()
    if q:
        products = products.filter(Q(name__icontains=q) | Q(sku__icontains=q))

    cat = request.GET.get('category')
    if cat:
        products = products.filter(category_id=cat)

    paginator = Paginator(products, 15)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    categories = Category.objects.all()

    return render(request, 'products/admin_product_list.html', {
        'products': page_obj,
        'categories': categories,
        'q': q,
        'selected_cat': cat,
    })


@user_passes_test(is_admin)
def admin_product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            
            # Handle primary gallery image upload
            primary_image_file = request.FILES.get('primary_image')
            if primary_image_file:
                ProductImage.objects.create(
                    product=product,
                    image=primary_image_file,
                    is_primary=True,
                    alt_text=f"{product.name} Primary View"
                )

            # Handle secondary angle image upload
            secondary_image_file = request.FILES.get('secondary_image')
            if secondary_image_file:
                ProductImage.objects.create(
                    product=product,
                    image=secondary_image_file,
                    is_primary=False,
                    alt_text=f"{product.name} Detail View",
                    sort_order=2
                )

            messages.success(request, f"Product '{product.name}' created successfully!")
            return redirect('admin_product_edit', pk=product.pk)
    else:
        form = ProductForm()

    return render(request, 'products/admin_product_form.html', {
        'form': form,
        'title': 'Add New Jewellery Product'
    })


@user_passes_test(is_admin)
def admin_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()

            # Upload new gallery image if provided
            new_image = request.FILES.get('new_gallery_image')
            if new_image:
                ProductImage.objects.create(
                    product=product,
                    image=new_image,
                    is_primary=False,
                    alt_text=request.POST.get('new_image_alt', product.name)
                )

            messages.success(request, f"Product '{product.name}' updated successfully.")
            return redirect('admin_product_edit', pk=product.pk)
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/admin_product_form.html', {
        'form': form,
        'product': product,
        'gallery_images': product.images.all(),
        'frames_360': product.images_360.all().order_by('frame_number'),
        'title': f"Edit Product: {product.name}"
    })


@user_passes_test(is_admin)
def admin_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f"Product '{name}' has been deleted.")
        return redirect('admin_product_list')
    return render(request, 'products/admin_product_confirm_delete.html', {'product': product})


@user_passes_test(is_admin)
def admin_360_upload(request, pk):
    """
    Dedicated 360-degree image sequence upload for administrators.
    Allows uploading multiple angle frames with sequential frame index.
    """
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        frames = request.FILES.getlist('frame_images')
        if frames:
            # Optionally clear existing frames if requested
            if request.POST.get('replace_existing') == '1':
                product.images_360.all().delete()
                start_frame = 1
            else:
                last_frame = product.images_360.order_by('-frame_number').first()
                start_frame = (last_frame.frame_number + 1) if last_frame else 1

            for i, f in enumerate(frames):
                Product360Image.objects.create(
                    product=product,
                    image=f,
                    frame_number=start_frame + i
                )

            messages.success(request, f"Successfully uploaded {len(frames)} 360-degree frame images for '{product.name}'!")
            return redirect('admin_360_upload', pk=product.pk)

    frames = product.images_360.all().order_by('frame_number')
    return render(request, 'products/admin_360_upload.html', {
        'product': product,
        'frames': frames
    })


@user_passes_test(is_admin)
def admin_delete_360_frame(request, frame_id):
    frame = get_object_or_404(Product360Image, id=frame_id)
    product_pk = frame.product.pk
    if request.method == 'POST':
        frame.delete()
        messages.success(request, "Frame deleted.")
    return redirect('admin_360_upload', pk=product_pk)


@user_passes_test(is_admin)
def admin_category_list(request):
    categories = Category.objects.all().order_by('display_order')
    return render(request, 'products/admin_category_list.html', {'categories': categories})


@user_passes_test(is_admin)
def admin_category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            cat = form.save()
            messages.success(request, f"Category '{cat.name}' created.")
            return redirect('admin_category_list')
    else:
        form = CategoryForm()
    return render(request, 'products/admin_category_form.html', {'form': form, 'title': 'Create Category'})


@user_passes_test(is_admin)
def admin_category_edit(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=cat)
        if form.is_valid():
            form.save()
            messages.success(request, f"Category '{cat.name}' updated.")
            return redirect('admin_category_list')
    else:
        form = CategoryForm(instance=cat)
    return render(request, 'products/admin_category_form.html', {'form': form, 'category': cat, 'title': f"Edit Category: {cat.name}"})


@user_passes_test(is_admin)
def admin_category_delete(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        name = cat.name
        cat.delete()
        messages.success(request, f"Category '{name}' deleted.")
        return redirect('admin_category_list')
    return render(request, 'products/admin_category_confirm_delete.html', {'category': cat})
