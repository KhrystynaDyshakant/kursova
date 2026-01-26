from django.contrib import admin
from django.utils.html import format_html
from .models import Contract, Vacancy, Candidate

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'salary_range', 'is_active_display', 'candidates_count', 'created_date']
    list_filter = ['department', 'is_active', 'created_date']
    search_fields = ['title', 'department', 'description']

    def salary_range(self, obj):
        return f"{obj.salary_from} - {obj.salary_to} грн"

    salary_range.short_description = 'Зарплата'

    def is_active_display(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Активна</span>')
        return format_html('<span style="color: red;">✗ Закрита</span>')

    is_active_display.short_description = 'Статус'

    def candidates_count(self, obj):
        count = obj.candidate_set.count()
        return format_html('<strong>{}</strong> кандидатів', count)

    candidates_count.short_description = 'Кандидати'


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'vacancy', 'email', 'phone', 'status_display', 'applied_date']
    list_filter = ['status', 'vacancy', 'applied_date']
    search_fields = ['first_name', 'last_name', 'email', 'vacancy__title']

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    full_name.short_description = "Ім'я"

    def status_display(self, obj):
        colors = {
            'new': '#2196f3',
            'review': '#ff9800',
            'interview': '#9c27b0',
            'offer': '#00bcd4',
            'hired': '#4caf50',
            'rejected': '#f44336',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 4px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )

    status_display.short_description = 'Статус'

    actions = ['mark_as_interview', 'mark_as_hired', 'mark_as_rejected']

    def mark_as_interview(self, request, queryset):
        queryset.update(status='interview')
        self.message_user(request, f"{queryset.count()} кандидатів запрошено на співбесіду")

    mark_as_interview.short_description = "Запросити на співбесіду"

    def mark_as_hired(self, request, queryset):
        queryset.update(status='hired')
        self.message_user(request, f"{queryset.count()} кандидатів прийнято")

    mark_as_hired.short_description = "Прийняти на роботу"

    def mark_as_rejected(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f"{queryset.count()} кандидатів відхилено")

    mark_as_rejected.short_description = "Відхилити"


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'position', 'salary', 'start_date', 'end_date', 'status_display']
    list_filter = ['position', 'status', 'start_date']
    search_fields = ['employee__first_name', 'employee__last_name', 'position']
    date_hierarchy = 'start_date'

    def status_display(self, obj):
        colors = {
            'pending': '#ff9800',
            'approved': '#4caf50',
            'rejected': '#f44336'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )

    status_display.short_description = 'Статус'
