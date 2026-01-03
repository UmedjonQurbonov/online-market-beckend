from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from .models import *
from .serializers import *
from .permissions import *
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import PermissionDenied
from .utils import update_shop_rating
from rest_framework import viewsets

class ShopViewSet(ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_permissions(self):
        if self.action == "create":
            return [IsSeller()]
        
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsSeller(), IsShopOwner()]

        return [AllowAny()]

    def get_queryset(self):        
        return Shop.objects.all()


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]

        return [IsAdminUser()]


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]

        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsSeller(), IsProductOwner()]

        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and user.role == "seller":
            return Product.objects.filter(shop__owner=user)

        return Product.objects.filter(is_active=True)    

class ProductImageViewSet(ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]

        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsSeller(), IsProductOwner()]

        return super().get_permissions()

    def perform_create(self, serializer):
        product = serializer.validated_data.get("product")

        if product.shop.owner != self.request.user:
            
            raise PermissionDenied("Вы не можете добавлять изображения к чужому товару.")

        serializer.save()    

class CartViewSet(ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get_permissions(self):
        user = self.request.user

        if not user.is_authenticated:
            return [IsAuthenticated()]

        if user.is_superuser:
            return [IsAuthenticated(), IsAdminUser()]

        return [IsAuthenticated(), IsCartOwner()]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Cart.objects.all()

        if user.role == "seller":
            return Cart.objects.none()

        return Cart.objects.filter(buyer=user)

    def perform_create(self, serializer):

        serializer.save(buyer=self.request.user)        

class CartItemViewSet(ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializator
    permission_classes = [IsAuthenticated, IsCartOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return CartItem.objects.all()

        return CartItem.objects.filter(cart__buyer=user)

    def perform_create(self, serializer):

        cart = serializer.validated_data['cart']

        if not self.request.user.is_staff and cart.buyer != self.request.user:
            raise PermissionDenied("Нельзя добавлять товары в чужую корзину")

        serializer.save()        

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_permissions(self):

        base = [IsAuthenticated()]
        if self.action in ["retrieve", "update", "partial_update", "destroy"]:
            base.append(IsOrderOwnerOrAdmin())

        return base

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Order.objects.all()

        return Order.objects.filter(buyer=user)

    def perform_create(self, serializer):
        serializer.save(buyer=self.request.user)

class OrderItemViewSet(ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

    def get_permissions(self):
        base = [IsAuthenticated()]

        if self.action in ["retrieve", "update", "partial_update", "destroy"]:
            base.append(IsOrderItemOwnerOrAdmin())

        return base

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return OrderItem.objects.all()

        return OrderItem.objects.filter(order__buyer=user)

class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        base = [IsAuthenticated()]

        if self.action in ["retrieve", "update", "partial_update", "destroy"]:
            base.append(IsReviewOwnerOrAdmin())

        return base

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Review.objects.all()

        return Review.objects.filter(author=user)

    def perform_create(self, serializer):
        review = serializer.save(author=self.request.user)
        update_shop_rating(review.shop)

    def perform_update(self, serializer):
        review = serializer.save()
        update_shop_rating(review.shop)

    def perform_destroy(self, instance):
        shop = instance.shop
        instance.delete()
        update_shop_rating(shop) 

class SellerOrderViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(
            cart__items__product__shop__owner=user
        ).distinct()