from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import random

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('Электронная почта'), unique=True)
    username = models.CharField(_('Имя пользователя'), max_length=150, blank=True)
    is_active = models.BooleanField(_('Активен'), default=False)
    is_staff = models.BooleanField(_('Статус персонала'), default=False)
    date_joined = models.DateTimeField(_('Дата регистрации'), default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

class ConfirmationCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='confirmation_code', verbose_name='Пользователь')
    code = models.CharField('Код подтверждения', max_length=6, unique=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    is_used = models.BooleanField('Использован', default=False)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = '{:06d}'.format(random.randint(0, 999999))
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.email} - {self.code} (used: {self.is_used})'

    class Meta:
        verbose_name = 'Код подтверждения'
        verbose_name_plural = 'Коды подтверждения'
