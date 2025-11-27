from django.contrib import admin
from .models import Document, Contract, LeaveRequest


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'document_type', 'created_date', 'status']
    list_filter = ['document_type', 'status']


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'position', 'salary', 'start_date', 'end_date']
    list_filter = ['position']
    search_fields = ['employee__first_name', 'employee__last_name']


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'leave_type', 'start_date', 'end_date']
    list_filter = ['leave_type']
    search_fields = ['employee__first_name', 'employee__last_name']