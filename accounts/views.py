from django.shortcuts import render
from rest_framework.response import Response
from .models import *
from rest_framework import status, generics
from .serializers import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        

        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Пользователь успешно зарегистрирован',
            'user': serializer.data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }
        }, status=status.HTTP_201_CREATED)
    

    
class VerifyCodeView(generics.GenericAPIView):
    serializer_class = VerifyCodeSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        user.is_active = True
        user.activation_code = None
        user.code_created_at = None
        user.save()

        return Response({"message": "Email подтверждён"}, status=status.HTTP_200_OK)
    

class EmailLoginView(generics.GenericAPIView):
    serializer_class = EmailLoginSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        tokens = serializer.create_tokens(user)
        return Response({
            'message': 'Успешный вход',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
            },
            'tokens': tokens
        }, status=status.HTTP_200_OK)
