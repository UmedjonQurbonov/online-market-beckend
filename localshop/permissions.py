from rest_framework.permissions import BasePermission

class IsSeller(BasePermission):
    message = "Только владельцы могут управлять магазинами."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "seller"
    
class IsShopOwner(BasePermission):
    message = "Вы можете изменять только свой магазин."

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class IsProductOwner(BasePermission):
    message = "Вы можете изменять только свои продукты."

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "shop"):
            return obj.shop.owner == request.user
        
        if hasattr(obj, "product"):
            return obj.product.shop.owner == request.user
        
        return False

class IsCartOwner(BasePermission):
    message = "Вы можете управлять только своей корзиной."

    def has_object_permission(self, request, view, obj):
        return obj.buyer == request.user    