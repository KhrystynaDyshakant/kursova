from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Sum, Avg
from datetime import datetime, date, timedelta

from .models import Employee
from requests.models import Request, PendingState, ApprovedState, RejectedState
from notifications.models import Notification
from timetracking.models import TimeRecord
from documents.models import Contract, LeaveRequest
from users.models import HR


def user_is_hr(user):
    return user.is_authenticated and user.role == 'hr'


@login_required
def hr_dashboard(request):
    if not user_is_hr(request.user):
        messages.error(request, 'Доступ заборонено. Тільки для HR.')
        return redirect('employee_dashboard')

    total_employees = Employee.objects.count()

    pending_ct = ContentType.objects.get_for_model(PendingState)
    pending_requests = Request.objects.filter(current_state_type=pending_ct).count()

    departments = Employee.objects.values('department').annotate(
        count=Count('id')
    ).order_by('-count')

    total_salary = sum([emp.get_salary() for emp in Employee.objects.all()])

    recent_requests = Request.objects.select_related('employee').order_by('-created_date')[:10]

    today = date.today()
    on_leave_today = LeaveRequest.objects.filter(
        start_date__lte=today,
        end_date__gte=today,
        status='approved'
    ).count()

    unread_count = 0

    context = {
        'total_employees': total_employees,
        'pending_requests': pending_requests,
        'departments': departments,
        'total_salary': total_salary,
        'recent_requests': recent_requests,
        'on_leave_today': on_leave_today,
        'unread_count': unread_count,
    }

    return render(request, 'hr/dashboard.html', context)


@login_required
def pending_requests(request):
    if not user_is_hr(request.user):
        messages.error(request, 'Доступ заборонено. Тільки для HR.')
        return redirect('employee_dashboard')

    pending_ct = ContentType.objects.get_for_model(PendingState)
    requests_list = Request.objects.filter(
        current_state_type=pending_ct
    ).select_related('employee').order_by('-created_date')

    unread_count = 0

    context = {
        'requests': requests_list,
        'unread_count': unread_count,
    }

    return render(request, 'hr/pending_requests.html', context)


@login_required
def approve_request(request, request_id):
    if not user_is_hr(request.user):
        messages.error(request, 'Доступ заборонено.')
        return redirect('employee_dashboard')

    req = get_object_or_404(Request, id=request_id)

    req.approve()

    Notification.objects.create(
        recipient=req.employee,
        notification_type='leave_approved',
        channel='push',
        message=f"Вашу заявку #{req.id} схвалено!",
        is_sent=True
    )

    print(f"[APPROVED] Заявка #{req.id} від {req.employee.first_name} {req.employee.last_name} СХВАЛЕНА HR: {request.user.username}")

    messages.success(request, f'Заявку #{req.id} схвалено! Співробітник отримав сповіщення.')
    return redirect('pending_requests')


@login_required
def reject_request(request, request_id):
    if not user_is_hr(request.user):
        messages.error(request, 'Доступ заборонено.')
        return redirect('employee_dashboard')

    req = get_object_or_404(Request, id=request_id)

    req.reject()

    Notification.objects.create(
        recipient=req.employee,
        notification_type='leave_rejected',
        channel='push',
        message=f"Вашу заявку #{req.id} відхилено. Зверніться до HR для деталей.",
        is_sent=True
    )

    print(f"[REJECTED] Заявка #{req.id} від {req.employee.first_name} {req.employee.last_name} ВІДХИЛЕНА HR: {request.user.username}")

    messages.warning(request, f'Заявку #{req.id} відхилено. Співробітник отримав сповіщення.')
    return redirect('pending_requests')


@login_required
def all_employees(request):
    if not user_is_hr(request.user):
        messages.error(request, 'Доступ заборонено.')
        return redirect('employee_dashboard')

    employees = Employee.objects.all()

    departments = Employee.objects.values('department').annotate(
        count=Count('id')
    ).order_by('-count')

    unread_count = 0

    context = {
        'employees': employees,
        'departments': departments,
        'unread_count': unread_count,
    }

    return render(request, 'hr/employees_list.html', context)


@login_required
def employee_detail(request, employee_id):
    if not user_is_hr(request.user):
        messages.error(request, 'Доступ заборонено.')
        return redirect('employee_dashboard')

    employee = get_object_or_404(Employee, id=employee_id)

    requests_list = Request.objects.filter(employee=employee).order_by('-created_date')[:10]

    month_start = date.today().replace(day=1)
    time_records = TimeRecord.objects.filter(
        employee=employee,
        date__gte=month_start
    ).order_by('-date')

    total_hours = sum([record.calculate_hours() for record in time_records])

    try:
        contract = Contract.objects.filter(employee=employee).latest('start_date')
    except Contract.DoesNotExist:
        contract = None

    unread_count = 0

    context = {
        'employee': employee,
        'requests': requests_list,
        'time_records': time_records,
        'total_hours': total_hours,
        'contract': contract,
        'unread_count': unread_count,
    }

    return render(request, 'hr/employee_detail.html', context)


@login_required
def reports(request):
    if not user_is_hr(request.user):
        messages.error(request, 'Доступ заборонено.')
        return redirect('employee_dashboard')

    departments_report = Employee.objects.values('department').annotate(
        count=Count('id')
    ).order_by('-count')

    salary_by_dept = {}
    for dept in departments_report:
        dept_employees = Employee.objects.filter(department=dept['department'])
        total = sum([emp.get_salary() for emp in dept_employees])
        salary_by_dept[dept['department']] = total

    pending_ct = ContentType.objects.get_for_model(PendingState)
    approved_ct = ContentType.objects.get_for_model(ApprovedState)
    rejected_ct = ContentType.objects.get_for_model(RejectedState)

    requests_stats = {
        'pending': Request.objects.filter(current_state_type=pending_ct).count(),
        'approved': Request.objects.filter(current_state_type=approved_ct).count(),
        'rejected': Request.objects.filter(current_state_type=rejected_ct).count(),
    }

    month_start = date.today().replace(day=1)
    month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    leaves_this_month = LeaveRequest.objects.filter(
        start_date__gte=month_start,
        start_date__lte=month_end
    ).count()

    unread_count = 0

    context = {
        'departments_report': departments_report,
        'salary_by_dept': salary_by_dept,
        'requests_stats': requests_stats,
        'leaves_this_month': leaves_this_month,
        'unread_count': unread_count,
    }

    return render(request, 'hr/reports.html', context)
