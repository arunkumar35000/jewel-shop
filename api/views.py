from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from products.models import Product, Product360Image
from cart.models import Cart, CartItem
from .serializers import ProductSerializer, Product360ImageSerializer, CartSerializer, CustomOrderSerializer
from custom_orders.models import CustomOrder


class ProductListAPI(generics.ListAPIView):
    queryset = Product.objects.filter(status='ACTIVE').select_related('category').prefetch_related('images')
    serializer_class = ProductSerializer


class ProductDetailAPI(generics.RetrieveAPIView):
    queryset = Product.objects.filter(status='ACTIVE').prefetch_related('images', 'images_360')
    serializer_class = ProductSerializer
    lookup_field = 'slug'


class Product360FramesAPI(APIView):
    """
    Returns the ordered list of 360 rotation frames for a given product slug.
    """
    def get(self, request, slug):
        product = Product.objects.filter(slug=slug).first()
        if not product:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        frames = product.images_360.all().order_by('frame_number')
        serializer = Product360ImageSerializer(frames, many=True, context={'request': request})
        return Response({
            'product_name': product.name,
            'total_frames': frames.count(),
            'frames': serializer.data
        })


class CartAPI(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.save()
                session_key = request.session.session_key
            cart, _ = Cart.objects.get_or_create(session_key=session_key)

        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data)


class CustomOrderListCreateAPI(generics.ListCreateAPIView):
    serializer_class = CustomOrderSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return CustomOrder.objects.filter(user=self.request.user)
        return CustomOrder.objects.none()

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)
