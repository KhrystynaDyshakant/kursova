from django.contrib import admin
from django.utils.html import format_html
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'recipient_info', 'notification_type_display', 'channel', 'status_display', 'created_at']
    list_filter = ['notification_type', 'channel', 'is_sent', 'is_read', 'created_at']
    search_fields = ['recipient__first_name', 'recipient__last_name', 'message']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']

    actions = ['mark_as_sent', 'mark_as_read']

    def recipient_info(self, obj):
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            f"{obj.recipient.first_name} {obj.recipient.last_name}",
            obj.recipient.email
        )

    recipient_info.short_description = 'Одержувач'

    def notification_type_display(self, obj):
        icons = {
            'order_created': '📝',
            'order_status': '🔄',
            'leave_approved': '✅',
            'leave_rejected': '❌',
        }
        icon = icons.get(obj.notification_type, '📬')
        return format_html(
            '{} {}',
            icon,
            obj.get_notification_type_display()
        )

    notification_type_display.short_description = 'Тип'

    def status_display(self, obj):
        if obj.is_read:
            return format_html('<span style="color: gray;">👁️ Прочитано</span>')
        elif obj.is_sent:
            return format_html('<span style="color: green;">✓ Надіслано</span>')
        else:
            return format_html('<span style="color: orange;">⏳ Очікує</span>')

    status_display.short_description = 'Статус'

    def mark_as_sent(self, request, queryset):
        updated = queryset.update(is_sent=True)
        self.message_user(request, f"{updated} сповіщень позначено як надіслані")

    mark_as_sent.short_description = "Позначити як надіслані"

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} сповіщень позначено як прочитані")

    mark_as_read.short_description = "Позначити як прочитані"