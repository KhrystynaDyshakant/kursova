from django.contrib import admin
from django.db.models import Count, Sum
from django.utils.html import format_html
from .models import Document, Contract, LeaveRequest, Order, Vacancy, Candidate


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'document_type', 'created_date', 'status_badge']
    list_filter = ['document_type', 'status', 'created_date']
    search_fields = ['id']

    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )

    status_badge.short_description = 'Статус'


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'position', 'salary', 'start_date', 'end_date']
    list_filter = ['position', 'start_date']
    search_fields = ['employee__first_name', 'employee__last_name', 'position']
    date_hierarchy = 'start_date'


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'leave_type', 'start_date', 'end_date', 'status', 'days_count']
    list_filter = ['leave_type', 'document__status', 'start_date']
    search_fields = ['employee__first_name', 'employee__last_name', 'reason']
    date_hierarchy = 'start_date'

    def status(self, obj):
        return obj.document.get_status_display()

    status.short_description = 'Статус'

    def days_count(self, obj):
        return (obj.end_date - obj.start_date).days + 1

    days_count.short_description = 'Днів'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'order_type', 'employee', 'order_date', 'created_by']
    list_filter = ['order_type', 'order_date']
    search_fields = ['order_number', 'employee__first_name', 'employee__last_name']
    date_hierarchy = 'order_date'


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'salary_range', 'is_active', 'candidates_count', 'created_date']
    list_filter = ['is_active', 'department', 'created_date']
    search_fields = ['title', 'department', 'description']

    def salary_range(self, obj):
        return f"{obj.salary_from} - {obj.salary_to} грн"

    salary_range.short_description = 'Зарплата'

    def candidates_count(self, obj):
        count = obj.candidate_set.count()
        return format_html('<strong>{}</strong>', count)

    candidates_count.short_description = 'Кандидатів'


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'vacancy', 'email', 'phone', 'status_badge', 'applied_date']
    list_filter = ['status', 'vacancy', 'applied_date']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    date_hierarchy = 'applied_date'

    actions = ['mark_as_interview', 'mark_as_offer', 'mark_as_hired', 'mark_as_rejected']

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    full_name.short_description = 'ПІБ'

    def status_badge(self, obj):
        colors = {
            'new': 'blue',
            'interview': 'orange',
            'offer': 'purple',
            'hired': 'green',
            'rejected': 'red'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )

    status_badge.short_description = 'Статус'

    # Масові дії
    def mark_as_interview(self, request, queryset):
        queryset.update(status='interview')
        self.message_user(request, f"{queryset.count()} кандидатів переведено на співбесіду")

    mark_as_interview.short_description = "→ На співбесіду"

    def mark_as_offer(self, request, queryset):
        queryset.update(status='offer')
        self.message_user(request, f"{queryset.count()} кандидатам надіслано оффер")

    mark_as_offer.short_description = "→ Надіслати оффер"

    def mark_as_hired(self, request, queryset):
        queryset.update(status='hired')
        self.message_user(request, f"{queryset.count()} кандидатів прийнято")

    mark_as_hired.short_description = "✓ Прийняти"

    def mark_as_rejected(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f"{queryset.count()} кандидатів відхилено")

    mark_as_rejected.short_description = "✗ Відхилити"