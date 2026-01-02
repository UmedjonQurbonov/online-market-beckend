from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from .models import Shop
from .serializers import ShopSerializer
from .permissions import IsSeller, IsShopOwner
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
