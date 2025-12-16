from django.contrib import admin
from django.shortcuts import render
from django.db.models import Count, Sum, Avg, Q
from django.utils.html import format_html
from datetime import date, timedelta
from employees.models import Employee
from requests.models import Request
from timetracking.models import TimeRecord
from documents.models import LeaveRequest, Vacancy, Candidate


class ReportsAdmin(admin.ModelAdmin):
    """Адмін інтерфейс для звітів"""

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        """Сторінка звітів"""

        # ===== ЗВІТ ПО ВІДДІЛАХ =====
        departments_report = Employee.objects.values('department').annotate(
            count=Count('id')
        ).order_by('-count')

        # Зарплати по відділах
        salary_by_dept = []
        for dept in departments_report:
            dept_employees = Employee.objects.filter(department=dept['department'])
            total_salary = sum([emp.get_salary() for emp in dept_employees])
            avg_salary = total_salary / dept['count'] if dept['count'] > 0 else 0

            salary_by_dept.append({
                'department': dept['department'],
                'count': dept['count'],
                'total_salary': total_salary,
                'avg_salary': avg_salary
            })

        # ===== ЗВІТ ПО ЗАЯВКАХ =====
        total_requests = Request.objects.count()
        pending_requests = Request.objects.filter(current_state__state_type='pending').count()
        approved_requests = Request.objects.filter(current_state__state_type='approved').count()
        rejected_requests = Request.objects.filter(current_state__state_type='rejected').count()

        # ===== ЗВІТ ПО ВІДПУСТКАХ =====
        today = date.today()
        month_start = today.replace(day=1)

        # Відпустки цього місяця
        leaves_this_month = LeaveRequest.objects.filter(
            start_date__gte=month_start,
            document__status='approved'
        ).count()

        # Співробітники у відпустці зараз
        on_leave_now = LeaveRequest.objects.filter(
            start_date__lte=today,
            end_date__gte=today,
            document__status='approved'
        ).count()

        # Заплановані відпустки
        future_leaves = LeaveRequest.objects.filter(
            start_date__gt=today,
            document__status='approved'
        ).order_by('start_date')[:10]

        # ===== ЗВІТ ПО РОБОЧОМУ ЧАСУ =====
        week_ago = today - timedelta(days=7)

        # Загальні години за тиждень
        week_records = TimeRecord.objects.filter(date__gte=week_ago)
        total_hours_week = sum([r.calculate_hours() for r in week_records])

        # Співробітники на роботі зараз
        on_work_now = TimeRecord.objects.filter(
            date=today,
            clock_out_time__isnull=True
        ).count()

        # Топ по годинах за тиждень
        from django.db.models import Sum as DbSum
        top_workers = []
        for emp in Employee.objects.all():
            emp_records = TimeRecord.objects.filter(employee=emp, date__gte=week_ago)
            hours = sum([r.calculate_hours() for r in emp_records])
            if hours > 0:
                top_workers.append({
                    'employee': emp,
                    'hours': hours
                })
        top_workers = sorted(top_workers, key=lambda x: x['hours'], reverse=True)[:10]

        # ===== ЗВІТ ПО ВАКАНСІЯХ =====
        active_vacancies = Vacancy.objects.filter(is_active=True).count()
        total_candidates = Candidate.objects.count()
        new_candidates = Candidate.objects.filter(status='new').count()

        # ===== ЗАГАЛЬНА СТАТИСТИКА =====
        total_employees = Employee.objects.count()
        total_salary = sum([emp.get_salary() for emp in Employee.objects.all()])

        extra_context = extra_context or {}
        extra_context.update({
            # Відділи та зарплати
            'salary_by_dept': salary_by_dept,
            'total_employees': total_employees,
            'total_salary': total_salary,

            # Заявки
            'total_requests': total_requests,
            'pending_requests': pending_requests,
            'approved_requests': approved_requests,
            'rejected_requests': rejected_requests,

            # Відпустки
            'leaves_this_month': leaves_this_month,
            'on_leave_now': on_leave_now,
            'future_leaves': future_leaves,

            # Робочий час
            'total_hours_week': round(total_hours_week, 1),
            'on_work_now': on_work_now,
            'top_workers': top_workers,

            # Вакансії
            'active_vacancies': active_vacancies,
            'total_candidates': total_candidates,
            'new_candidates': new_candidates,
        })

        return render(request, 'admin/reports.html', extra_context)


# Реєстрація "фейкової" моделі для звітів
from django.apps import apps


class Reports:
    class _meta:
        app_label = 'employees'
        model_name = 'reports'
        verbose_name = '📊 Звіти та аналітика'
        verbose_name_plural = '📊 Звіти та аналітика'
        object_name = 'Reports'

    @classmethod
    def _meta(cls):
        return cls._meta


try:
    admin.site.register(Reports, ReportsAdmin)
except:
    pass