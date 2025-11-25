from django.contrib import admin
from .models import Request, RequestState


@admin.register(RequestState)
class RequestStateAdmin(admin.ModelAdmin):
    list_display = ['id', 'state_type']
    list_filter = ['state_type']


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'current_state', 'created_date']
    list_filter = ['current_state']
    search_fields = ['employee__first_name', 'employee__last_name']