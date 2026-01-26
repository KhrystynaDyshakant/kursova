from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, HR


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active']
    search_fields = ['username', 'email']

    fieldsets = (
        ('Основна інформація', {
            'fields': ('username', 'email', 'password')
        }),
        ('Роль', {
            'fields': ('role',)
        }),
        ('Права доступу', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Важливі дати', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )


@admin.register(HR)
class HRAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_display', 'email_display']
    search_fields = ['name', 'email']

    def name_display(self, obj):
        return obj.name if hasattr(obj, 'name') else f"HR #{obj.id}"

    name_display.short_description = 'Ім\'я'

    def email_display(self, obj):
        return obj.email if hasattr(obj, 'email') else '-'

    email_display.short_description = 'Email'