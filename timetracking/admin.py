from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from datetime import date, timedelta
from .models import TimeRecord


@admin.register(TimeRecord)
class TimeRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee_info', 'date', 'clock_in_time', 'clock_out_time', 'hours_worked', 'status']
    list_filter = ['date', 'employee__department']
    search_fields = ['employee__first_name', 'employee__last_name']
    date_hierarchy = 'date'

    def employee_info(self, obj):
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            f"{obj.employee.first_name} {obj.employee.last_name}",
            obj.employee.department
        )

    employee_info.short_description = 'Співробітник'

    def hours_worked(self, obj):
        hours = obj.calculate_hours()
        if hours >= 8:
            color = 'green'
        elif hours >= 6:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f} год</span>',
            color, hours
        )

    hours_worked.short_description = 'Відпрацьовано'

    def status(self, obj):
        if obj.clock_out_time:
            return format_html('<span style="color: green;">✓ Завершено</span>')
        else:
            return format_html('<span style="color: orange;">⏰ На роботі</span>')

    status.short_description = 'Статус'

    # Звіти
    def changelist_view(self, request, extra_context=None):
        # Загальна статистика
        today = date.today()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        # Сьогодні на роботі
        on_work_now = TimeRecord.objects.filter(
            date=today,
            clock_out_time__isnull=True
        ).count()

        # Загальні години за тиждень
        week_records = TimeRecord.objects.filter(date__gte=week_ago)
        total_hours_week = sum([r.calculate_hours() for r in week_records])

        # Загальні години за місяць
        month_records = TimeRecord.objects.filter(date__gte=month_ago)
        total_hours_month = sum([r.calculate_hours() for r in month_records])

        extra_context = extra_context or {}
        extra_context['on_work_now'] = on_work_now
        extra_context['total_hours_week'] = round(total_hours_week, 1)
        extra_context['total_hours_month'] = round(total_hours_month, 1)

        return super().changelist_view(request, extra_context=extra_context)