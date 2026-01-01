from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from .views import *


urlpatterns = [
    path('register/', RegisterView.as_view()),
    path("verify/", VerifyCodeView.as_view()),
    path('auth/login/', EmailLoginView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    ]