from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.db.models import Count, Sum
from employees.models import Employee
from requests.models import Request
from timetracking.models import TimeRecord
from documents.models import LeaveRequest, Vacancy, Candidate
from datetime import date, timedelta


class HRMAdminSite(admin.AdminSite):
    site_header = "HRM System - Панель HR"
    site_title = "HRM Admin"
    index_title = "Управління персоналом"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('reports/', self.admin_view(self.reports_view), name='hrm_reports'),
        ]
        return custom_urls + urls

    def reports_view(self, request):
        """Сторінка звітів"""
        today = date.today()
        month_start = today.replace(day=1)

        # Звіт по відділах
        departments = Employee.objects.values('department').annotate(
            count=Count('id')
        ).order_by('-count')

        # Зарплати по відділах
        salary_by_dept = {}
        for dept in departments:
            dept_employees = Employee.objects.filter(department=dept['department'])
            total = sum([emp.get_salary() for emp in dept_employees])
            salary_by_dept[dept['department']] = {
                'count': dept['count'],
                'total_salary': total,
                'avg_salary': total / dept['count'] if dept['count'] > 0 else 0
            }

        # Заявки
        requests_stats = Request.objects.values('current_state__state_type').annotate(
            count=Count('id')
        )

        # Відпустки цього місяця
        leaves_count = LeaveRequest.objects.filter(
            start_date__gte=month_start
        ).count()

        # Вакансії та кандидати
        active_vacancies = Vacancy.objects.filter(is_active=True).count()
        total_candidates = Candidate.objects.count()
        new_candidates = Candidate.objects.filter(status='new').count()

        context = {
            'salary_by_dept': salary_by_dept,
            'requests_stats': list(requests_stats),
            'leaves_count': leaves_count,
            'active_vacancies': active_vacancies,
            'total_candidates': total_candidates,
            'new_candidates': new_candidates,
            'total_employees': Employee.objects.count(),
        }

        return render(request, 'admin/reports.html', context)


# Використати кастомний AdminSite
hrm_admin_site = HRMAdminSite(name='hrm_admin')