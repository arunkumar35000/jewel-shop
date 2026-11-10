from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import HeroBanner, Testimonial, Subscriber, ContactInquiry
from products.models import Product, Category


def home(request):
    """
    Luxury Jewellery Homepage view rendering all promotional sections.
    """
    banners = HeroBanner.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True).order_by('display_order')[:6]
    
    new_arrivals = Product.objects.filter(status='ACTIVE', is_new=True).prefetch_related('images')[:8]
    trending_products = Product.objects.filter(status='ACTIVE', is_trending=True).prefetch_related('images')[:8]
    bestsellers = Product.objects.filter(status='ACTIVE', is_bestseller=True).prefetch_related('images')[:8]
    
    bridal_collection = Product.objects.filter(status='ACTIVE', category__slug='bridal-trousseau').prefetch_related('images')[:4]
    diamond_collection = Product.objects.filter(status='ACTIVE', category__slug='diamond-solitaires').prefetch_related('images')[:4]
    gold_collection = Product.objects.filter(status='ACTIVE', category__slug='gold-jewellery').prefetch_related('images')[:4]
    
    testimonials = Testimonial.objects.filter(is_featured=True)[:6]

    context = {
        'banners': banners,
        'categories': categories,
        'new_arrivals': new_arrivals,
        'trending_products': trending_products,
        'bestsellers': bestsellers,
        'bridal_collection': bridal_collection,
        'diamond_collection': diamond_collection,
        'gold_collection': gold_collection,
        'testimonials': testimonials,
    }
    return render(request, 'core/home.html', context)


def newsletter_subscribe(request):
    """
    Newsletter subscription handler with AJAX JSON and standard POST support.
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if not email or '@' not in email:
            if request.is_ajax() or request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Please provide a valid email address.'}, status=400)
            messages.error(request, 'Please provide a valid email address.')
            return redirect('home')

        subscriber, created = Subscriber.objects.get_or_create(email=email)
        msg = "Thank you for subscribing to Aura Royal Insider! Exclusive jewellery previews await you." if created else "You are already subscribed to Aura Royal Insider."

        if request.is_ajax() or request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': msg})

        messages.success(request, msg)
        return redirect('home')

    return redirect('home')


def about(request):
    return render(request, 'core/about.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')

        ContactInquiry.objects.create(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message_text
        )
        messages.success(request, 'Your message has been sent to our flagship jewellery concierge. We will contact you within 24 hours.')
        return redirect('contact')

    return render(request, 'core/contact.html')
