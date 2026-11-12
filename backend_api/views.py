from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count, Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status, permissions

from products.models import Product, Product360Image, Category
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem
from custom_orders.models import CustomOrder, CustomOrderImage, CustomOrderQuotation
from .serializers import (
    ProductSerializer, Product360ImageSerializer, CategorySerializer,
    CartSerializer, CustomOrderSerializer, OrderSerializer, CustomerDirectorySerializer
)


# Helper function to get or create cart
def _get_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.save()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


# =====================================================================
# WEBSITE CLIENT APIS
# =====================================================================

class CategoryListAPI(generics.ListAPIView):
    """
    Returns active product categories for website navigation & filters.
    """
    queryset = Category.objects.filter(is_active=True).order_by('display_order')
    serializer_class = CategorySerializer


class ProductListAPI(generics.ListAPIView):
    """
    Product Catalog API with multi-facet filters, search, and sorting.
    Query params: q, category, metal, purity, min_price, max_price, has_360, sort
    """
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = Product.objects.filter(status='ACTIVE').select_related('category').prefetch_related('images', 'images_360')
        
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(name__icontains=q) |
                Q(description__icontains=q) |
                Q(sku__icontains=q) |
                Q(category__name__icontains=q)
            )

        category = self.request.GET.get('category')
        if category:
            qs = qs.filter(Q(category__slug=category) | Q(category_id=category))

        metal = self.request.GET.get('metal')
        if metal:
            qs = qs.filter(metal_type=metal)

        purity = self.request.GET.get('purity')
        if purity:
            qs = qs.filter(purity=purity)

        min_price = self.request.GET.get('min_price')
        if min_price:
            qs = qs.filter(base_price__gte=Decimal(min_price))

        max_price = self.request.GET.get('max_price')
        if max_price:
            qs = qs.filter(base_price__lte=Decimal(max_price))

        has_360 = self.request.GET.get('has_360')
        if has_360 == '1':
            qs = qs.filter(images_360__isnull=False).distinct()

        sort = self.request.GET.get('sort', 'newest')
        if sort == 'price_asc':
            qs = qs.order_by('base_price')
        elif sort == 'price_desc':
            qs = qs.order_by('-base_price')
        elif sort == 'bestseller':
            qs = qs.order_by('-is_bestseller', '-created_at')
        elif sort == 'discount':
            qs = qs.order_by('-discount_percent', '-created_at')
        else:
            qs = qs.order_by('-created_at')

        return qs


class ProductDetailAPI(generics.RetrieveAPIView):
    """
    Returns single product details by slug, including full image gallery.
    """
    queryset = Product.objects.filter(status='ACTIVE').prefetch_related('images', 'images_360')
    serializer_class = ProductSerializer
    lookup_field = 'slug'


class Product360FramesAPI(APIView):
    """
    Returns the ordered list of 360-degree rotation multi-angle image frames.
    """
    def get(self, request, slug):
        product = Product.objects.filter(slug=slug).first()
        if not product:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        frames = product.images_360.all().order_by('frame_number')
        serializer = Product360ImageSerializer(frames, many=True, context={'request': request})
        return Response({
            'product_name': product.name,
            'sku': product.sku,
            'total_frames': frames.count(),
            'frames': serializer.data
        })


class CartAPI(APIView):
    """
    Retrieves the current shopping bag with subtotal, GST, and grand total.
    """
    def get(self, request):
        cart = _get_cart(request)
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data)


class CartItemAddAPI(APIView):
    """
    Adds a jewellery product to the shopping bag.
    """
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        if not product_id:
            return Response({'error': 'product_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id, status='ACTIVE')
        cart = _get_cart(request)

        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = max(1, quantity)
        item.save()

        return Response({
            'success': True,
            'message': f"Added '{product.name}' to shopping bag",
            'total_items': cart.total_items,
            'grand_total': str(cart.grand_total)
        }, status=status.HTTP_200_OK)


class CartItemUpdateAPI(APIView):
    """
    Updates the quantity of an existing item in the shopping cart.
    Accepts item_id in URL, and {"quantity": 2} or {"action": "increase"|"decrease"}.
    """
    def post(self, request, item_id):
        cart = _get_cart(request)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        action = request.data.get('action')
        quantity = request.data.get('quantity')

        if action == 'increase':
            item.quantity += 1
            item.save()
        elif action == 'decrease':
            if item.quantity > 1:
                item.quantity -= 1
                item.save()
            else:
                item.delete()
        elif quantity is not None:
            try:
                qty = int(quantity)
                if qty > 0:
                    item.quantity = qty
                    item.save()
                else:
                    item.delete()
            except (ValueError, TypeError):
                return Response({'error': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'success': True,
            'message': 'Shopping bag updated successfully',
            'total_items': cart.total_items,
            'grand_total': str(cart.grand_total)
        }, status=status.HTTP_200_OK)


class CartItemRemoveAPI(APIView):
    """
    Removes an item from the shopping bag by item_id.
    """
    def post(self, request, item_id):
        cart = _get_cart(request)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        name = item.product.name
        item.delete()
        return Response({
            'success': True,
            'message': f"Removed '{name}' from shopping bag",
            'total_items': cart.total_items,
            'grand_total': str(cart.grand_total)
        }, status=status.HTTP_200_OK)

    def delete(self, request, item_id):
        return self.post(request, item_id)


# =====================================================================
# USER AUTHENTICATION & SESSION APIS
# =====================================================================

class AuthLoginAPI(APIView):
    """
    Authenticates user and initiates an active Django session.
    Accepts {"username": "...", "password": "..."}.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({'error': 'Both username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_active:
                return Response({'error': 'Account is inactive.'}, status=status.HTTP_403_FORBIDDEN)
            login(request, user)
            if not request.session.session_key:
                request.session.save()
            return Response({
                'success': True,
                'message': f"Welcome, {user.username}!",
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser
                },
                'session_key': request.session.session_key
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)


class AuthLogoutAPI(APIView):
    """
    Terminates the user's active session.
    """
    def post(self, request):
        logout(request)
        return Response({'success': True, 'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)


class AuthUserAPI(APIView):
    """
    Returns current authenticated user details.
    """
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'authenticated': False, 'user': None}, status=status.HTTP_200_OK)
        return Response({
            'authenticated': True,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'is_staff': request.user.is_staff
            }
        }, status=status.HTTP_200_OK)


class OrderTrackAPI(APIView):
    """
    Public order tracking endpoint by order_number.
    """
    def get(self, request, order_number):
        order = Order.objects.filter(order_number=order_number).first()
        if not order:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'order_number': order.order_number,
            'order_status': order.order_status,
            'status_display': order.get_order_status_display(),
            'tracking_number': order.tracking_number,
            'courier_partner': order.courier_partner,
            'estimated_delivery': order.estimated_delivery,
            'grand_total': str(order.grand_total),
            'items_count': order.items.count()
        })


class CustomOrderListCreateAPI(generics.ListCreateAPIView):
    """
    Custom design requests API. Authenticated users list requests; anyone can POST a request.
    """
    serializer_class = CustomOrderSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return CustomOrder.objects.filter(user=self.request.user).prefetch_related('reference_images', 'quotations')
        return CustomOrder.objects.none()

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)


# =====================================================================
# ADMIN PANEL COMMUNICATION APIS
# =====================================================================

class AdminDashboardStatsAPI(APIView):
    """
    Provides real-time KPI metrics and sales breakdown for the Admin Dashboard & Chart.js.
    """
    def get(self, request):
        if not (request.user.is_authenticated and request.user.is_staff):
            return Response({'error': 'Unauthorized. Admin credentials required.'}, status=status.HTTP_403_FORBIDDEN)

        total_orders = Order.objects.count()
        total_sales = Order.objects.filter(payment_status='PAID').aggregate(s=Sum('grand_total'))['s'] or Decimal('0.00')
        total_customers = User.objects.filter(is_staff=False).count()
        total_custom_requests = CustomOrder.objects.count()
        pending_orders = Order.objects.filter(order_status__in=['PENDING', 'CONFIRMED']).count()
        pending_custom_requests = CustomOrder.objects.filter(status__in=['PENDING', 'UNDER_REVIEW']).count()

        # Sales category distribution for Chart.js
        categories = Category.objects.filter(is_active=True)
        cat_labels = [c.name for c in categories]
        cat_sales = []
        for cat in categories:
            val = OrderItem.objects.filter(product__category=cat).aggregate(s=Sum('total_price'))['s'] or Decimal('0.00')
            cat_sales.append(float(val))

        return Response({
            'kpis': {
                'total_sales': str(total_sales),
                'total_orders': total_orders,
                'total_customers': total_customers,
                'total_custom_requests': total_custom_requests,
                'pending_orders': pending_orders,
                'pending_custom_requests': pending_custom_requests,
            },
            'charts': {
                'category_labels': cat_labels,
                'category_sales': cat_sales,
            }
        })


class AdminOrderListAPI(generics.ListAPIView):
    """
    Admin orders management API with search and status filtering.
    """
    serializer_class = OrderSerializer

    def get_queryset(self):
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            return Order.objects.none()

        qs = Order.objects.all().order_by('-created_at').prefetch_related('items')
        order_status = self.request.GET.get('status')
        if order_status:
            qs = qs.filter(order_status=order_status)

        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(order_number__icontains=q) |
                Q(customer_name__icontains=q) |
                Q(customer_phone__icontains=q)
            )
        return qs


class AdminOrderStatusUpdateAPI(APIView):
    """
    Allows Admin Panel to update order lifecycle status, courier partner, and tracking ID.
    """
    def patch(self, request, order_number):
        if not (request.user.is_authenticated and request.user.is_staff):
            return Response({'error': 'Admin credentials required'}, status=status.HTTP_403_FORBIDDEN)

        order = get_object_or_404(Order, order_number=order_number)
        new_status = request.data.get('order_status')
        tracking_number = request.data.get('tracking_number')
        courier_partner = request.data.get('courier_partner')

        if new_status:
            order.order_status = new_status
        if tracking_number:
            order.tracking_number = tracking_number
        if courier_partner:
            order.courier_partner = courier_partner

        order.save()
        return Response({
            'success': True,
            'message': f"Order #{order.order_number} updated to {order.get_order_status_display()}",
            'order_status': order.order_status,
            'tracking_number': order.tracking_number
        })


class AdminCustomerListAPI(generics.ListAPIView):
    """
    Admin customer directory with total purchases & lifetime value.
    """
    serializer_class = CustomerDirectorySerializer

    def get_queryset(self):
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            return User.objects.none()

        return User.objects.filter(is_staff=False).annotate(
            orders_count=Count('orders'),
            total_spent=Sum('orders__grand_total')
        ).order_by('-date_joined')
