from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login
from .models import User, ConfirmationCode
from .serializers import RegisterSerializer, LoginSerializer, ConfirmSerializer
from django.utils.translation import gettext_lazy as _

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': _('Регистрация успешна. Проверьте email для подтверждения.')}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            # Для API не используем login(request, user), просто возвращаем успех
            return Response({'message': _('Успешная авторизация')}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ConfirmView(APIView):
    def post(self, request):
        serializer = ConfirmSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            conf = serializer.validated_data['conf']
            user.is_active = True
            user.save()
            conf.is_used = True
            conf.save()
            return Response({'message': _('Пользователь успешно подтверждён и активирован')}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
