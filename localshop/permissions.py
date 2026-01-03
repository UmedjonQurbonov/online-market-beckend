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
    
class IsCartOwnerOrAdmin(BasePermission):
    message = "Можно управлять только своей корзиной."

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True

        return obj.cart.buyer == request.user    

class IsOrderOwnerOrAdmin(BasePermission):
    message = "Вы можете управлять только своими заказами."

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        return obj.buyer == request.user    

class IsOrderItemOwnerOrAdmin(BasePermission):
    message = "Вы можете управлять только товарами в своих заказах."

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        return obj.order.buyer == request.user    
    

class IsReviewOwnerOrAdmin(BasePermission):
    message = "Вы можете управлять только своими отзывами."

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.author == request.user