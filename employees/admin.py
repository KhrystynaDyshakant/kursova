from django.contrib import admin
from django.db.models import Count, Sum, Avg
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from datetime import date, timedelta
from .models import Employee, FixedSalaryStrategy, BonusSalaryStrategy


@admin.register(FixedSalaryStrategy)
class FixedSalaryStrategyAdmin(admin.ModelAdmin):
    list_display = ['id', 'monthly_amount']
    search_fields = ['monthly_amount']

    class Meta:
        verbose_name = 'Стратегія: Фіксована'
        verbose_name_plural = 'Стратегії: Фіксовані'


@admin.register(BonusSalaryStrategy)
class BonusSalaryStrategyAdmin(admin.ModelAdmin):
    list_display = ['id', 'base_salary', 'bonus_percentage']
    search_fields = ['base_salary']

    class Meta:
        verbose_name = 'Стратегія: З бонусами'
        verbose_name_plural = 'Стратегії: З бонусами'


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'position', 'department', 'salary_display', 'hire_date', 'work_duration']
    list_filter = ['department', 'position', 'hire_date']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    date_hierarchy = 'hire_date'

    fieldsets = (
        ('Особиста інформація', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Робоча інформація', {
            'fields': ('position', 'department', 'hire_date', 'salary_strategy_type', 'salary_strategy_id')
        }),
    )

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    full_name.short_description = 'ПІБ'

    def salary_display(self, obj):
        salary = obj.get_salary()
        return format_html('<strong>{} грн</strong>', salary)

    salary_display.short_description = 'Зарплата'

    def work_duration(self, obj):
        from datetime import date
        delta = date.today() - obj.hire_date
        years = delta.days // 365
        months = (delta.days % 365) // 30
        return f"{years} р. {months} міс."

    work_duration.short_description = 'Стаж'


class ReportsProxy(Employee):
    class Meta:
        proxy = True
        verbose_name = 'Звіти та аналітика'
        verbose_name_plural = 'Звіти та аналітика'


@admin.register(ReportsProxy)
class ReportsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        from requests.models import Request, PendingState, ApprovedState, RejectedState
        from timetracking.models import TimeRecord
        from django.contrib.contenttypes.models import ContentType

        departments_report = Employee.objects.values('department').annotate(
            count=Count('id')
        ).order_by('-count')

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

        total_requests = Request.objects.count()

        pending_ct = ContentType.objects.get_for_model(PendingState)
        approved_ct = ContentType.objects.get_for_model(ApprovedState)
        rejected_ct = ContentType.objects.get_for_model(RejectedState)

        pending_requests = Request.objects.filter(current_state_type=pending_ct).count()
        approved_requests = Request.objects.filter(current_state_type=approved_ct).count()
        rejected_requests = Request.objects.filter(current_state_type=rejected_ct).count()

        today = date.today()
        week_ago = today - timedelta(days=7)

        week_records = TimeRecord.objects.filter(date__gte=week_ago)
        total_hours_week = sum([r.calculate_hours() for r in week_records])

        on_work_now = TimeRecord.objects.filter(
            date=today,
            clock_out_time__isnull=True
        ).count()

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

        total_employees = Employee.objects.count()
        total_salary = sum([emp.get_salary() for emp in Employee.objects.all()])

        # Вакансії та кандидати
        from documents.models import Vacancy, Candidate, LeaveRequest

        active_vacancies = Vacancy.objects.filter(is_active=True).count()
        total_candidates = Candidate.objects.count()
        new_candidates = Candidate.objects.filter(status='new').count()

        # Відпустки цього місяця
        month_start = today.replace(day=1)
        leaves_this_month = LeaveRequest.objects.filter(
            start_date__gte=month_start
        ).count()

        # Зараз у відпустці
        on_leave_now = LeaveRequest.objects.filter(
            start_date__lte=today,
            end_date__gte=today,
            status='approved'
        ).count()

        extra_context = extra_context or {}
        extra_context.update({
            'salary_by_dept': salary_by_dept,
            'total_employees': total_employees,
            'total_salary': total_salary,
            'total_requests': total_requests,
            'pending_requests': pending_requests,
            'approved_requests': approved_requests,
            'rejected_requests': rejected_requests,
            'total_hours_week': round(total_hours_week, 1),
            'on_work_now': on_work_now,
            'top_workers': top_workers,
            'active_vacancies': active_vacancies,
            'total_candidates': total_candidates,
            'new_candidates': new_candidates,
            'leaves_this_month': leaves_this_month,
            'on_leave_now': on_leave_now,
            'title': 'Звіти та аналітика',
            'app_label': 'employees',
        })

        return render(request, 'admin/reports.html', extra_context)
