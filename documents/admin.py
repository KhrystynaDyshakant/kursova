from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from .models import Document, Contract, LeaveRequest, Order, Vacancy, Candidate


# ========== LEAVE REQUESTS (Заявки на відпустку) ==========

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee_info', 'leave_type_display', 'dates_info', 'days_count_display', 'status_display',
                    'created_date']
    list_filter = ['leave_type', 'document__status', 'start_date']
    search_fields = ['employee__first_name', 'employee__last_name', 'reason']
    date_hierarchy = 'start_date'
    readonly_fields = ['document', 'created_date_display']

    fieldsets = (
        ('Інформація про співробітника', {
            'fields': ('employee',)
        }),
        ('Деталі відпустки', {
            'fields': ('leave_type', 'reason', 'start_date', 'end_date')
        }),
        ('Документ', {
            'fields': ('document', 'created_date_display')
        }),
    )

    def employee_info(self, obj):
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            f"{obj.employee.first_name} {obj.employee.last_name}",
            obj.employee.department
        )

    employee_info.short_description = 'Співробітник'

    def leave_type_display(self, obj):
        icons = {
            'vacation': '🏖️',
            'sick': '🏥',
        }
        return format_html(
            '{} {}',
            icons.get(obj.leave_type, '📋'),
            obj.get_leave_type_display()
        )

    leave_type_display.short_description = 'Тип'

    def dates_info(self, obj):
        return format_html(
            '{} - {}',
            obj.start_date.strftime('%d.%m.%Y'),
            obj.end_date.strftime('%d.%m.%Y')
        )

    dates_info.short_description = 'Період'

    def days_count_display(self, obj):
        days = (obj.end_date - obj.start_date).days + 1
        return format_html('<strong>{} днів</strong>', days)

    days_count_display.short_description = 'Тривалість'

    def status_display(self, obj):
        colors = {
            'pending': '#ff9800',
            'approved': '#4caf50',
            'rejected': '#f44336'
        }
        status = obj.document.status
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 12px; border-radius: 4px; font-weight: bold;">{}</span>',
            colors.get(status, 'gray'),
            obj.document.get_status_display()
        )

    status_display.short_description = 'Статус'

    def created_date(self, obj):
        return obj.document.created_date

    created_date.short_description = 'Дата створення'

    def created_date_display(self, obj):
        return obj.document.created_date

    created_date_display.short_description = 'Дата створення'

    def has_add_permission(self, request):
        """Заборонити створення вручну - тільки через Factory"""
        return False


# ========== CONTRACTS ==========

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'position', 'salary', 'start_date', 'end_date', 'status_display']
    list_filter = ['position', 'start_date']
    search_fields = ['employee__first_name', 'employee__last_name', 'position']
    date_hierarchy = 'start_date'
    readonly_fields = ['document']

    def status_display(self, obj):
        colors = {
            'pending': '#ff9800',
            'approved': '#4caf50',
            'rejected': '#f44336'
        }
        status = obj.document.status
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(status, 'gray'),
            obj.document.get_status_display()
        )

    status_display.short_description = 'Статус'


# ========== ORDERS ==========

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'order_type_display', 'employee', 'order_date', 'created_by']
    list_filter = ['order_type', 'order_date']
    search_fields = ['order_number', 'employee__first_name', 'employee__last_name']
    date_hierarchy = 'order_date'

    def order_type_display(self, obj):
        icons = {
            'vacation': '🏖️',
            'hire': '✅',
            'fire': '❌',
            'promotion': '⬆️',
        }
        icon = icons.get(obj.order_type, '📄')
        return format_html('{} {}', icon, obj.get_order_type_display())

    order_type_display.short_description = 'Тип наказу'


# ========== VACANCIES ==========

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


# ========== CANDIDATES ==========

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