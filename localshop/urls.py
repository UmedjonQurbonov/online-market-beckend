from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'shops', ShopViewSet, basename='shop')
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"products", ProductViewSet, basename="product")
router.register(r"product-images", ProductImageViewSet, basename="product-image")
router.register(r"carts", CartViewSet, basename="cart")
router.register(r'cart-items', CartItemViewSet, basename='cartitem')
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"order-items", OrderItemViewSet, basename="order-item")
router.register(r"review", ReviewViewSet, basename="review")

urlpatterns = [
    path('', include(router.urls)),
]