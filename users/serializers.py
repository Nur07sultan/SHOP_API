from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, ConfirmationCode
from django.utils.translation import gettext_lazy as _

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6, max_length=128)
    class Meta:
        model = User
        fields = ('email', 'username', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data.get('username', ''),
            password=validated_data['password'],
            is_active=False
        )
        ConfirmationCode.objects.create(user=user)
        return user

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Пользователь с таким email уже существует')
        return value

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Неверный email или пароль')
        if not user.is_active:
            raise serializers.ValidationError('Пользователь не активирован')
        data['user'] = user
        return data

class ConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            user = User.objects.get(email__iexact=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError('Пользователь не найден')
        try:
            conf = ConfirmationCode.objects.get(user=user, code=data['code'], is_used=False)
        except ConfirmationCode.DoesNotExist:
            raise serializers.ValidationError('Неверный или уже использованный код')
        data['user'] = user
        data['conf'] = conf
        return data
