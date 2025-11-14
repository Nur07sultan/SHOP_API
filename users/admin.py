from django.contrib import admin
from .models import User, ConfirmationCode

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'username')
    list_filter = ('is_active', 'is_staff')

@admin.register(ConfirmationCode)
class ConfirmationCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'is_used')
    search_fields = ('user__email', 'code')
    list_filter = ('is_used',)
