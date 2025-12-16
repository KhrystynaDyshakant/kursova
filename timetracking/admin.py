from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from datetime import date, timedelta
from .models import TimeRecord


@admin.register(TimeRecord)
class TimeRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee_info', 'date', 'clock_in_display', 'clock_out_display', 'hours_worked', 'status']
    list_filter = ['date', 'employee__department']
    search_fields = ['employee__first_name', 'employee__last_name']
    date_hierarchy = 'date'
    readonly_fields = ['date', 'clock_in_time']

    fieldsets = (
        ('Інформація про співробітника', {
            'fields': ('employee',)
        }),
        ('Час', {
            'fields': ('date', 'clock_in_time', 'clock_out_time')
        }),
    )

    def employee_info(self, obj):
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            f"{obj.employee.first_name} {obj.employee.last_name}",
            obj.employee.department
        )

    employee_info.short_description = 'Співробітник'

    def clock_in_display(self, obj):
        """Відображення часу приходу"""
        if obj.clock_in_time:
            return obj.clock_in_time.strftime('%H:%M:%S')
        return '-'

    clock_in_display.short_description = 'Прихід'

    def clock_out_display(self, obj):
        """Відображення часу виходу"""
        if obj.clock_out_time:
            return obj.clock_out_time.strftime('%H:%M:%S')
        return '-'

    clock_out_display.short_description = 'Вихід'

    def hours_worked(self, obj):
        """Відображення відпрацьованих годин"""
        hours = obj.calculate_hours()

        if hours >= 8:
            color = 'green'
        elif hours >= 6:
            color = 'orange'
        else:
            color = 'red'

        # ВИПРАВЛЕНО: спочатку форматуємо число, потом передаємо в format_html
        hours_str = f'{hours:.1f} год'

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            hours_str
        )

    hours_worked.short_description = 'Відпрацьовано'

    def status(self, obj):
        if obj.clock_out_time:
            return format_html('<span style="color: green;">✓ Завершено</span>')
        else:
            return format_html('<span style="color: orange;">⏰ На роботі</span>')

    status.short_description = 'Статус'

    def has_add_permission(self, request):
        """Заборонити додавання записів вручну (створюються через Clock In/Out)"""
        return False