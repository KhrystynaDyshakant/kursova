from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from .models import Request, RequestState
from notifications.models import Notification


@admin.register(RequestState)
class RequestStateAdmin(admin.ModelAdmin):
    list_display = ['id', 'state_type_display']

    def state_type_display(self, obj):
        colors = {
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.state_type, 'gray'),
            obj.get_state_type_display()
        )

    state_type_display.short_description = 'Статус'


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee_info', 'request_type_display', 'dates_info', 'current_state_display',
                    'created_date', 'quick_actions']
    list_filter = ['current_state__state_type', 'request_type', 'created_date', 'employee__department']
    search_fields = ['employee__first_name', 'employee__last_name', 'reason']
    date_hierarchy = 'created_date'
    readonly_fields = ['created_date']

    fieldsets = (
        ('Основна інформація', {
            'fields': ('employee', 'request_type', 'reason')
        }),
        ('Дати', {
            'fields': ('start_date', 'end_date')
        }),
        ('Статус', {
            'fields': ('current_state', 'hr_comment')
        }),
    )

    actions = ['approve_selected', 'reject_selected']

    def employee_info(self, obj):
        return format_html(
            '<strong>{}</strong><br><small>{} - {}</small>',
            f"{obj.employee.first_name} {obj.employee.last_name}",
            obj.employee.position,
            obj.employee.department
        )

    employee_info.short_description = 'Співробітник'

    def request_type_display(self, obj):
        icons = {
            'vacation': '🏖️',
            'sick': '🏥',
            'remote': '💻',
            'other': '📋'
        }
        return format_html(
            '{} {}',
            icons.get(obj.request_type, '📋'),
            obj.get_request_type_display()
        )

    request_type_display.short_description = 'Тип'

    def dates_info(self, obj):
        if obj.start_date and obj.end_date:
            days = obj.days_count()
            return format_html(
                '{} - {}<br><small>({} днів)</small>',
                obj.start_date.strftime('%d.%m.%Y'),
                obj.end_date.strftime('%d.%m.%Y'),
                days
            )
        return '-'

    dates_info.short_description = 'Період'

    def current_state_display(self, obj):
        if not obj.current_state:
            return format_html('<span style="color: gray;">Без статусу</span>')

        colors = {
            'pending': '#ff9800',
            'approved': '#4caf50',
            'rejected': '#f44336'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 12px; border-radius: 4px; font-weight: bold; display: inline-block;">{}</span>',
            colors.get(obj.current_state.state_type, 'gray'),
            obj.current_state.get_state_type_display()
        )

    current_state_display.short_description = 'Статус'

    def quick_actions(self, obj):
        if obj.current_state and obj.current_state.state_type == 'pending':
            # ВАЖЛИВО: використовуємо правильний формат URL
            approve_url = f'/admin/requests/request/{obj.pk}/approve/'
            reject_url = f'/admin/requests/request/{obj.pk}/reject/'

            return format_html(
                '<div style="display: flex; gap: 5px; flex-wrap: nowrap;">'
                '<a href="{}" style="background: #4caf50; color: white; padding: 8px 15px; border-radius: 4px; text-decoration: none; font-weight: bold; white-space: nowrap;">✓ Схвалити</a>'
                '<a href="{}" style="background: #f44336; color: white; padding: 8px 15px; border-radius: 4px; text-decoration: none; font-weight: bold; white-space: nowrap;">✗ Відхилити</a>'
                '</div>',
                approve_url, reject_url
            )
        elif obj.current_state and obj.current_state.state_type == 'approved':
            return format_html('<span style="color: green; font-weight: bold;">✓ Схвалено</span>')
        elif obj.current_state and obj.current_state.state_type == 'rejected':
            return format_html('<span style="color: red; font-weight: bold;">✗ Відхилено</span>')
        return '-'

    quick_actions.short_description = 'Дії'

    # Масові дії
    def approve_selected(self, request, queryset):
        approved_state = RequestState.objects.get(state_type='approved')
        count = 0

        for req in queryset:
            if req.current_state and req.current_state.state_type == 'pending':
                req.current_state = approved_state
                req.save()

                # Створити сповіщення
                Notification.objects.create(
                    recipient=req.employee,
                    notification_type='leave_approved',
                    channel='push',
                    message=f"✅ Вашу заявку #{req.id} ({req.get_request_type_display()}) схвалено!",
                    is_sent=True
                )

                print(
                    f"✅ [HR APPROVED] Заявка #{req.id} ({req.get_request_type_display()}) від {req.employee.first_name} {req.employee.last_name} СХВАЛЕНА")
                count += 1

        self.message_user(request, f"✅ Схвалено {count} заявок. Співробітники отримали сповіщення.", messages.SUCCESS)

    approve_selected.short_description = "✓ Схвалити обрані заявки"

    def reject_selected(self, request, queryset):
        rejected_state = RequestState.objects.get(state_type='rejected')
        count = 0

        for req in queryset:
            if req.current_state and req.current_state.state_type == 'pending':
                req.current_state = rejected_state
                req.save()

                # Створити сповіщення
                Notification.objects.create(
                    recipient=req.employee,
                    notification_type='leave_rejected',
                    channel='push',
                    message=f"❌ Вашу заявку #{req.id} ({req.get_request_type_display()}) відхилено. Зверніться до HR.",
                    is_sent=True
                )

                print(
                    f"❌ [HR REJECTED] Заявка #{req.id} ({req.get_request_type_display()}) від {req.employee.first_name} {req.employee.last_name} ВІДХИЛЕНА")
                count += 1

        self.message_user(request, f"❌ Відхилено {count} заявок. Співробітники отримали сповіщення.", messages.WARNING)

    reject_selected.short_description = "✗ Відхилити обрані заявки"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<int:request_id>/approve/', self.admin_site.admin_view(self.approve_request_view),
                 name='approve_request'),
            path('<int:request_id>/reject/', self.admin_site.admin_view(self.reject_request_view),
                 name='reject_request'),
        ]
        return custom_urls + urls

    def approve_request_view(self, request, request_id):
        """Швидке схвалення заявки"""
        req = Request.objects.get(pk=request_id)

        print(f"\n{'=' * 50}")
        print(f"🔵 ПОЧАТОК СХВАЛЕННЯ")
        print(f"Заявка ID: {req.id}")
        print(f"Співробітник: {req.employee.first_name} {req.employee.last_name}")
        print(f"Email: {req.employee.email}")

        approved_state = RequestState.objects.get(state_type='approved')
        req.current_state = approved_state
        req.save()

        print(f"✅ Статус змінено на: {approved_state.get_state_type_display()}")

        # Створити сповіщення
        notification = Notification.objects.create(
            recipient=req.employee,
            notification_type='leave_approved',
            channel='push',
            message=f"✅ Вашу заявку #{req.id} ({req.get_request_type_display()}) схвалено!",
            is_sent=True,
            is_read=False
        )

        print(f"📬 Сповіщення створено:")
        print(f"   ID: {notification.id}")
        print(f"   Одержувач: {notification.recipient}")
        print(f"   Повідомлення: {notification.message}")
        print(f"   is_sent: {notification.is_sent}")
        print(f"   is_read: {notification.is_read}")
        print(f"{'=' * 50}\n")

        messages.success(request, f"✅ Заявку #{req.id} схвалено! Співробітник отримав сповіщення.")
        return redirect('admin:requests_request_changelist')

    def reject_request_view(self, request, request_id):
        """Швидке відхилення заявки"""
        req = Request.objects.get(pk=request_id)
        rejected_state = RequestState.objects.get(state_type='rejected')
        req.current_state = rejected_state
        req.save()

        # Сповіщення
        notification = Notification.objects.create(
            recipient=req.employee,
            notification_type='leave_rejected',
            channel='push',
            message=f"❌ Вашу заявку #{req.id} ({req.get_request_type_display()}) відхилено. Зверніться до HR.",
            is_sent=True,
            is_read=False  # ← ВАЖЛИВО!
        )

        print(f"❌ [HR REJECTED] Заявка #{req.id} ВІДХИЛЕНА - Сповіщення #{notification.id} створено")

        messages.warning(request, f"❌ Заявку #{req.id} відхилено! Співробітник отримав сповіщення.")
        return redirect('admin:requests_request_changelist')