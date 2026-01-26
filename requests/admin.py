from django.contrib import admin
from django.utils.html import format_html
from django.contrib.contenttypes.models import ContentType
from django import forms
from .models import Request, PendingState, ApprovedState, RejectedState

class RequestAdminForm(forms.ModelForm):
    STATE_CHOICES = [
        ('pending', 'Очікує'),
        ('approved', 'Схвалено'),
        ('rejected', 'Відхилено'),
    ]
    state = forms.ChoiceField(choices=STATE_CHOICES, label='Стан')

    class Meta:
        model = Request
        fields = ['employee', 'request_type', 'reason', 'start_date', 'end_date', 'hr_comment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.current_state_type:
                model = self.instance.current_state_type.model
                if 'pending' in model:
                    self.fields['state'].initial = 'pending'
                elif 'approved' in model:
                    self.fields['state'].initial = 'approved'
                elif 'rejected' in model:
                    self.fields['state'].initial = 'rejected'

    def save(self, commit=True):
        instance = super().save(commit=False)
        state_value = self.cleaned_data.get('state')

        if state_value == 'pending':
            state, _ = PendingState.objects.get_or_create(pk=1)
            instance.current_state_type = ContentType.objects.get_for_model(PendingState)
            instance.current_state_id = state.id
        elif state_value == 'approved':
            state, _ = ApprovedState.objects.get_or_create(pk=1)
            instance.current_state_type = ContentType.objects.get_for_model(ApprovedState)
            instance.current_state_id = state.id
        elif state_value == 'rejected':
            state, _ = RejectedState.objects.get_or_create(pk=1)
            instance.current_state_type = ContentType.objects.get_for_model(RejectedState)
            instance.current_state_id = state.id

        if commit:
            instance.save()
        return instance


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    form = RequestAdminForm
    list_display = ['id', 'employee_info', 'request_type_display', 'dates_info', 'status_display', 'created_date']
    list_filter = ['request_type', 'created_date']
    search_fields = ['employee__first_name', 'employee__last_name', 'reason']
    date_hierarchy = 'created_date'

    fieldsets = (
        ('Співробітник', {
            'fields': ('employee',)
        }),
        ('Деталі заявки', {
            'fields': ('request_type', 'reason', 'start_date', 'end_date')
        }),
        ('Стан', {
            'fields': ('state', 'hr_comment')
        }),
    )

    actions = ['approve_requests', 'reject_requests']

    def employee_info(self, obj):
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            f"{obj.employee.first_name} {obj.employee.last_name}",
            obj.employee.department
        )

    employee_info.short_description = 'Співробітник'

    def request_type_display(self, obj):
        icons = {
            'vacation': '🏖️',
            'sick': '🏥',
            'remote': '🏠',
            'other': '📋',
        }
        return format_html(
            '{} {}',
            icons.get(obj.request_type, '📋'),
            obj.get_request_type_display()
        )

    request_type_display.short_description = 'Тип'

    def dates_info(self, obj):
        if obj.start_date and obj.end_date:
            return format_html(
                '{} - {}',
                obj.start_date.strftime('%d.%m.%Y'),
                obj.end_date.strftime('%d.%m.%Y')
            )
        return '-'

    dates_info.short_description = 'Період'

    def status_display(self, obj):
        if not obj.current_state:
            return format_html('<span style="color: gray;">Невизначено</span>')

        pending_ct = ContentType.objects.get_for_model(PendingState)
        approved_ct = ContentType.objects.get_for_model(ApprovedState)
        rejected_ct = ContentType.objects.get_for_model(RejectedState)

        if obj.current_state_type == pending_ct:
            return format_html(
                '<span style="background-color: #ff9800; color: white; padding: 5px 12px; border-radius: 4px;">Очікує</span>')
        elif obj.current_state_type == approved_ct:
            return format_html(
                '<span style="background-color: #4caf50; color: white; padding: 5px 12px; border-radius: 4px;">Схвалено</span>')
        elif obj.current_state_type == rejected_ct:
            return format_html(
                '<span style="background-color: #f44336; color: white; padding: 5px 12px; border-radius: 4px;">Відхилено</span>')
        return str(obj.current_state)

    status_display.short_description = 'Статус'

    def approve_requests(self, request, queryset):
        from notifications.models import Notification
        for req in queryset:
            old_state_type = req.current_state_type
            req.approve()
            # Створити сповіщення
            Notification.objects.create(
                recipient=req.employee,
                notification_type='leave_approved',
                channel='push',
                message=f'Вашу заявку #{req.id} схвалено!',
                is_sent=True
            )
        self.message_user(request, f"{queryset.count()} заявок схвалено")

    approve_requests.short_description = "Схвалити вибрані заявки"

    def reject_requests(self, request, queryset):
        from notifications.models import Notification
        for req in queryset:
            req.reject()
            # Створити сповіщення
            Notification.objects.create(
                recipient=req.employee,
                notification_type='leave_rejected',
                channel='push',
                message=f'Вашу заявку #{req.id} відхилено.',
                is_sent=True
            )
        self.message_user(request, f"{queryset.count()} заявок відхилено")

    reject_requests.short_description = "Відхилити вибрані заявки"

    def save_model(self, request, obj, form, change):
        from notifications.models import Notification

        old_state = None
        if change and obj.pk:
            try:
                old_obj = Request.objects.get(pk=obj.pk)
                old_state = old_obj.current_state_type
            except Request.DoesNotExist:
                pass

        super().save_model(request, obj, form, change)

        # Якщо стан змінився - створити сповіщення
        if change and old_state and old_state != obj.current_state_type:
            approved_ct = ContentType.objects.get_for_model(ApprovedState)
            rejected_ct = ContentType.objects.get_for_model(RejectedState)

            if obj.current_state_type == approved_ct:
                Notification.objects.create(
                    recipient=obj.employee,
                    notification_type='leave_approved',
                    channel='push',
                    message=f'Вашу заявку #{obj.id} схвалено!',
                    is_sent=True
                )
            elif obj.current_state_type == rejected_ct:
                Notification.objects.create(
                    recipient=obj.employee,
                    notification_type='leave_rejected',
                    channel='push',
                    message=f'Вашу заявку #{obj.id} відхилено.',
                    is_sent=True
                )
