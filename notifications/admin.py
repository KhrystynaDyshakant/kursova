from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'recipient', 'notification_type', 'channel', 'is_sent', 'is_read', 'created_at']
    list_filter = ['notification_type', 'channel', 'is_sent', 'is_read']
    search_fields = ['recipient__first_name', 'recipient__last_name', 'message']