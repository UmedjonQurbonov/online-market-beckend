from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from .models import *
from .serializers import *
from .permissions import *
from rest_framework.parsers import MultiPartParser, FormParser

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
            return [IsSeller() | IsAdminUser(), IsProductOwner()]

        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and user.role == "seller":
            return Product.objects.filter(shop__owner=user)

        return Product.objects.filter(is_active=True)    

class ProductImageViewSet(ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]

        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsSeller(), IsProductOwner()]

        return super().get_permissions()

    def perform_create(self, serializer):
        product = serializer.validated_data.get("product")

        if product.shop.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
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