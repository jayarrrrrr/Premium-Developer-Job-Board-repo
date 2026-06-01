from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, Profile


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Premium', {'fields': ('is_premium', 'premium_activated_at', 'premium_expires_at')}),
    )
    list_display = ('username', 'email', 'is_premium', 'premium_activated_at', 'premium_expires_at', 'is_staff')
    list_filter = ('is_premium', 'is_staff', 'is_superuser')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_premium', 'created_at')
    list_filter = ('role', 'is_premium')
