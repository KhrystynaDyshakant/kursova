from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, HR


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'is_active', 'is_staff']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Додаткова інформація', {
            'fields': ('role', 'phone', 'email_notifications', 'sms_notifications')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Додаткова інформація', {
            'fields': ('role', 'phone')
        }),
    )


@admin.register(HR)
class HRAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'user', 'departments_display']
    list_filter = ['managed_departments']
    search_fields = ['name', 'email', 'user__username']

    def departments_display(self, obj):
        if obj.managed_departments:
            return ', '.join(obj.managed_departments)
        return '-'

    departments_display.short_description = 'Відділи'
