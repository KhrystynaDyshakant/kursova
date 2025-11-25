from django.contrib import admin
from .models import Employee, SalaryStrategy


@admin.register(SalaryStrategy)
class SalaryStrategyAdmin(admin.ModelAdmin):
    list_display = ['id', 'strategy_type', 'monthly_amount', 'base_salary', 'bonus_percentage']
    list_filter = ['strategy_type']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'position', 'department', 'hire_date']
    list_filter = ['department', 'position']
    search_fields = ['first_name', 'last_name', 'email']