from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, HR


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Додаткова інформація', {'fields': ('role', 'phone', 'email_notifications', 'sms_notifications')}),
    )


@admin.register(HR)
class HRAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'get_departments']

    def get_departments(self, obj):
        return ', '.join(obj.managed_departments) if obj.managed_departments else '-'

    get_departments.short_description = 'Відділи'