from django.contrib import admin
from django.utils.html import format_html
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
        from documents.models import DocumentFactory  # ← ДОДАТИ ІМПОРТ

        approved_state = RequestState.objects.get(state_type='approved')
        count = 0
        docs_created = 0

        for req in queryset.filter(current_state__state_type='pending'):
            req.current_state = approved_state
            req.save()

            # Створити сповіщення
            notification = Notification.objects.create(
                recipient=req.employee,
                notification_type='leave_approved',
                channel='push',
                message=f"✅ Вашу заявку #{req.id} ({req.get_request_type_display()}) схвалено!",
                is_sent=True,
                is_read=False
            )

            # ========== FACTORY PATTERN ==========
            if req.request_type in ['vacation', 'sick'] and req.start_date and req.end_date:
                try:
                    leave_document = DocumentFactory.create_document(
                        document_type='leave_request',
                        employee=req.employee,
                        leave_type=req.request_type,
                        reason=req.reason or f"Заявка #{req.id}",
                        start_date=req.start_date,
                        end_date=req.end_date
                    )
                    leave_document.document.status = 'approved'
                    leave_document.document.save()
                    docs_created += 1

                    print(f"📄 [FACTORY] Документ #{leave_document.id} створено для заявки #{req.id}")
                except Exception as e:
                    print(f"⚠️ Помилка Factory для заявки #{req.id}: {e}")

            print(f"\n{'=' * 60}")
            print(f"✅ [HR APPROVED VIA ACTION] Заявка #{req.id}")
            print(f"   Співробітник: {req.employee.first_name} {req.employee.last_name}")
            print(f"   Сповіщення #{notification.id} створено")
            print(f"{'=' * 60}\n")

            count += 1

        success_msg = f"✅ Схвалено {count} заявок. Співробітники отримали сповіщення."
        if docs_created > 0:
            success_msg += f" Створено {docs_created} офіційних документів через Factory Pattern."

        self.message_user(request, success_msg, messages.SUCCESS)

    def reject_selected(self, request, queryset):
        rejected_state = RequestState.objects.get(state_type='rejected')
        count = 0

        for req in queryset.filter(current_state__state_type='pending'):
            req.current_state = rejected_state
            req.save()

            # Створити сповіщення - ВИПРАВЛЕНО is_read=False
            notification = Notification.objects.create(
                recipient=req.employee,
                notification_type='leave_rejected',
                channel='push',
                message=f"❌ Вашу заявку #{req.id} ({req.get_request_type_display()}) відхилено.",
                is_sent=True,
                is_read=False  # ← ВИПРАВЛЕНО!
            )

            print(f"\n{'=' * 60}")
            print(f"❌ [HR REJECTED VIA ACTION] Заявка #{req.id}")
            print(f"   Співробітник: {req.employee.first_name} {req.employee.last_name}")
            print(f"   Сповіщення #{notification.id} створено")
            print(f"{'=' * 60}\n")

            count += 1

        self.message_user(request, f"❌ Відхилено {count} заявок. Співробітники отримали сповіщення.", messages.WARNING)

    reject_selected.short_description = "✗ Відхилити обрані заявки"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/approve/', self.admin_site.admin_view(self.approve_view),
                 name='requests_request_approve'),
            path('<path:object_id>/reject/', self.admin_site.admin_view(self.reject_view),
                 name='requests_request_reject'),
        ]
        return custom_urls + urls

    def approve_view(self, request, object_id):
        """Схвалити заявку + створити офіційний документ через Factory"""
        from documents.models import DocumentFactory  # ← ДОДАТИ ІМПОРТ

        req = Request.objects.get(pk=object_id)
        approved_state = RequestState.objects.get(state_type='approved')
        req.current_state = approved_state
        req.save()

        # Створити сповіщення
        notification = Notification.objects.create(
            recipient=req.employee,
            notification_type='leave_approved',
            channel='push',
            message=f"✅ Вашу заявку #{req.id} ({req.get_request_type_display()}) схвалено!",
            is_sent=True,
            is_read=False
        )

        # ========== FACTORY PATTERN ==========
        # Створити офіційний документ через Factory для відпусток та лікарняних
        leave_document = None
        if req.request_type in ['vacation', 'sick'] and req.start_date and req.end_date:
            try:
                leave_document = DocumentFactory.create_document(
                    document_type='leave_request',
                    employee=req.employee,
                    leave_type=req.request_type,
                    reason=req.reason or f"Заявка #{req.id}",
                    start_date=req.start_date,
                    end_date=req.end_date
                )
                # Одразу схвалюємо документ
                leave_document.document.status = 'approved'
                leave_document.document.save()

                print(f"\n{'=' * 60}")
                print(f"📄 [FACTORY PATTERN USED] Створено офіційний документ")
                print(f"   Request ID: #{req.id}")
                print(f"   LeaveRequest ID: #{leave_document.id}")
                print(f"   Document ID: #{leave_document.document.id}")
                print(f"{'=' * 60}")
            except Exception as e:
                print(f"⚠️ Помилка створення документа через Factory: {e}")

        print(f"\n{'=' * 60}")
        print(f"✅ [HR APPROVED] Заявка #{req.id}")
        print(f"   Співробітник: {req.employee.first_name} {req.employee.last_name}")
        print(f"   Email: {req.employee.email}")
        print(f"   Сповіщення #{notification.id} створено")
        print(f"   Повідомлення: {notification.message}")
        print(f"   is_sent: {notification.is_sent}, is_read: {notification.is_read}")
        if leave_document:
            print(f"   Офіційний документ: LeaveRequest #{leave_document.id}")
        print(f"{'=' * 60}\n")

        success_msg = f"✅ Заявку #{req.id} схвалено! Співробітник отримав сповіщення."
        if leave_document:
            success_msg += f" Створено офіційний документ #{leave_document.id}."

        messages.success(request, success_msg)
        return redirect('admin:requests_request_changelist')

    def reject_view(self, request, object_id):
        """Відхилити заявку"""
        req = Request.objects.get(pk=object_id)
        rejected_state = RequestState.objects.get(state_type='rejected')
        req.current_state = rejected_state
        req.save()

        # Створити сповіщення - ВИПРАВЛЕНО is_read=False
        notification = Notification.objects.create(
            recipient=req.employee,
            notification_type='leave_rejected',
            channel='push',
            message=f"❌ Вашу заявку #{req.id} ({req.get_request_type_display()}) відхилено.",
            is_sent=True,
            is_read=False  # ← ВИПРАВЛЕНО!
        )

        print(f"\n{'=' * 60}")
        print(f"❌ [HR REJECTED] Заявка #{req.id}")
        print(f"   Сповіщення #{notification.id} створено")
        print(f"{'=' * 60}\n")

        messages.warning(request, f"❌ Заявку #{req.id} відхилено! Співробітник отримав сповіщення.")
        return redirect('admin:requests_request_changelist')