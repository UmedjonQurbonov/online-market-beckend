from rest_framework.permissions import BasePermission

class IsSeller(BasePermission):
    message = "Только владельцы (seller) могут управлять магазинами."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "seller"
    
class IsShopOwner(BasePermission):
    message = "Вы можете изменять только свой магазин."

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
