from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None,               {'fields': ('username', 'password')}),
        ('Персональные данные', {'fields': ('first_name', 'last_name', 'email', 'role')}),
        ('Права',            {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты',      {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter  = ('role', 'is_staff', 'is_superuser', 'is_active')
