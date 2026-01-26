from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, date
from django.utils import timezone

from .models import Employee
from requests.models import Request, PendingState, ApprovedState, RejectedState
from notifications.models import Notification
from timetracking.models import TimeRecord, TimeTrackingSystem


@login_required
def employee_dashboard(request):
    if hasattr(request.user, 'role') and request.user.role == 'hr':
        return redirect('/admin/')

    if request.user.is_superuser:
        messages.warning(request, 'Ви увійшли як адміністратор. Використовуйте /admin/')
        return redirect('/admin/')

    try:
        employee = Employee.objects.get(email=request.user.email)
    except Employee.DoesNotExist:
        messages.error(request, f'Співробітника з email {request.user.email} не знайдено. Зверніться до HR.')
        return redirect('login')

    total_requests = Request.objects.filter(employee=employee).count()

    pending_ct = ContentType.objects.get_for_model(PendingState)
    approved_ct = ContentType.objects.get_for_model(ApprovedState)

    pending_requests = Request.objects.filter(
        employee=employee,
        current_state_type=pending_ct
    ).count()
    approved_requests = Request.objects.filter(
        employee=employee,
        current_state_type=approved_ct
    ).count()

    recent_requests = Request.objects.filter(employee=employee).order_by('-created_date')[:5]

    recent_notifications = Notification.objects.filter(
        recipient=employee,
        is_read=False
    ).order_by('-created_at')[:3]

    unread_count = Notification.objects.filter(
        recipient=employee,
        is_read=False
    ).count()

    today = timezone.now().date()
    time_system = TimeTrackingSystem.get_instance()

    today_record = TimeRecord.objects.filter(
        employee=employee,
        date=today,
        clock_out_time__isnull=True
    ).first()

    is_clocked_in = today_record is not None

    today_hours = 0
    all_today_records = TimeRecord.objects.filter(employee=employee, date=today)
    for record in all_today_records:
        today_hours += record.calculate_hours()

    if is_clocked_in and today_record:
        now = timezone.now()
        current_delta = now - today_record.clock_in_time
        current_hours = current_delta.total_seconds() / 3600
        today_hours = float(today_hours) + current_hours

    today_hours = round(float(today_hours), 1)

    week_start = today - timezone.timedelta(days=today.weekday())
    week_records = TimeRecord.objects.filter(
        employee=employee,
        date__gte=week_start
    )
    week_hours = sum([r.calculate_hours() for r in week_records])
    week_hours = round(week_hours, 1)

    context = {
        'employee': employee,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'recent_requests': recent_requests,
        'recent_notifications': recent_notifications,
        'unread_count': unread_count,
        'is_clocked_in': is_clocked_in,
        'today_hours': today_hours,
        'week_hours': week_hours,
        'today_record': today_record,
    }

    return render(request, 'employee/dashboard.html', context)


@login_required
def clock_in(request):
    try:
        employee = Employee.objects.get(email=request.user.email)
    except Employee.DoesNotExist:
        messages.error(request, 'Співробітника не знайдено')
        return redirect('login')

    time_system = TimeTrackingSystem.get_instance()
    today = date.today()

    existing = TimeRecord.objects.filter(
        employee=employee,
        date=today,
        clock_out_time__isnull=True
    ).exists()

    if existing:
        messages.warning(request, 'Ви вже відмітили прихід сьогодні!')
    else:
        record = time_system.clock_in(employee)
        messages.success(request, f'Прихід зафіксовано о {record.clock_in_time.strftime("%H:%M")}')
        print(f"[CLOCK IN] {employee.first_name} {employee.last_name} - {datetime.now().strftime('%H:%M:%S')}")

    return redirect('employee_dashboard')


@login_required
def clock_out(request):
    try:
        employee = Employee.objects.get(email=request.user.email)
    except Employee.DoesNotExist:
        messages.error(request, 'Співробітника не знайдено')
        return redirect('login')

    time_system = TimeTrackingSystem.get_instance()
    record = time_system.clock_out(employee)

    if record:
        hours = record.calculate_hours()
        messages.success(request, f'Вихід зафіксовано! Відпрацьовано: {hours} год.')
        print(
            f"[CLOCK OUT] {employee.first_name} {employee.last_name} - {datetime.now().strftime('%H:%M:%S')} - Відпрацьовано: {hours} год.")
    else:
        messages.error(request, 'Спочатку потрібно відмітити прихід!')

    return redirect('employee_dashboard')


@login_required
def submit_request(request):
    try:
        employee = Employee.objects.get(email=request.user.email)
    except Employee.DoesNotExist:
        messages.error(request, 'Співробітника не знайдено')
        return redirect('login')

    if request.method == 'POST':
        request_type = request.POST.get('request_type')
        reason = request.POST.get('reason', '')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        pending_state, _ = PendingState.objects.get_or_create(pk=1)
        pending_ct = ContentType.objects.get_for_model(PendingState)

        new_request = Request.objects.create(
            employee=employee,
            request_type=request_type,
            reason=reason,
            start_date=start_date if start_date else None,
            end_date=end_date if end_date else None,
            current_state_type=pending_ct,
            current_state_id=pending_state.id
        )

        print(
            f"[NEW REQUEST] Заявка #{new_request.id} ({new_request.get_request_type_display()}) від {employee.first_name} {employee.last_name}")

        messages.success(request, f'Заявку #{new_request.id} успішно подано! Очікуйте на розгляд HR.')
        return redirect('my_requests')

    unread_count = Notification.objects.filter(
        recipient=employee,
        is_read=False
    ).count()

    return render(request, 'employee/submit_request.html', {
        'employee': employee,
        'unread_count': unread_count
    })


@login_required
def my_requests(request):
    try:
        employee = Employee.objects.get(email=request.user.email)
    except Employee.DoesNotExist:
        messages.error(request, 'Співробітника не знайдено')
        return redirect('login')

    requests_list = Request.objects.filter(employee=employee).order_by('-created_date')

    unread_count = Notification.objects.filter(
        recipient=employee,
        is_read=False
    ).count()

    return render(request, 'employee/my_requests.html', {
        'employee': employee,
        'requests': requests_list,
        'unread_count': unread_count
    })


@login_required
def notifications_view(request):
    try:
        employee = Employee.objects.get(email=request.user.email)
    except Employee.DoesNotExist:
        messages.error(request, 'Співробітника не знайдено')
        return redirect('login')

    notifications = Notification.objects.filter(
        recipient=employee
    ).order_by('-created_at')

    unread_count = notifications.filter(is_read=False).count()

    return render(request, 'employee/notifications.html', {
        'employee': employee,
        'notifications': notifications,
        'unread_count': unread_count
    })


@login_required
def mark_as_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.is_read = True
        notification.save()
        messages.success(request, 'Сповіщення позначено як прочитане')
    except Notification.DoesNotExist:
        messages.error(request, 'Сповіщення не знайдено')

    return redirect('notifications')


@login_required
def request_detail(request, request_id):
    from django.contrib.contenttypes.models import ContentType
    from requests.models import PendingState, ApprovedState, RejectedState

    try:
        employee = Employee.objects.get(email=request.user.email)
    except Employee.DoesNotExist:
        messages.error(request, 'Співробітника не знайдено')
        return redirect('login')

    try:
        req = Request.objects.get(id=request_id, employee=employee)
    except Request.DoesNotExist:
        messages.error(request, 'Заявку не знайдено')
        return redirect('my_requests')

    # Визначаємо статус
    request_status = 'unknown'
    if req.current_state_type:
        pending_ct = ContentType.objects.get_for_model(PendingState)
        approved_ct = ContentType.objects.get_for_model(ApprovedState)
        rejected_ct = ContentType.objects.get_for_model(RejectedState)

        if req.current_state_type == pending_ct:
            request_status = 'pending'
        elif req.current_state_type == approved_ct:
            request_status = 'approved'
        elif req.current_state_type == rejected_ct:
            request_status = 'rejected'

    unread_count = Notification.objects.filter(
        recipient=employee,
        is_read=False
    ).count()

    return render(request, 'employee/request_detail.html', {
        'employee': employee,
        'request': req,
        'request_status': request_status,
        'unread_count': unread_count
    })


@login_required
def my_salary(request):
    from datetime import timedelta
    from timetracking.models import TimeRecord

    try:
        employee = Employee.objects.get(email=request.user.email)
    except Employee.DoesNotExist:
        messages.error(request, 'Співробітника не знайдено')
        return redirect('login')

    current_salary = employee.get_salary()
    strategy = employee.salary_strategy

    # Визначаємо тип стратегії
    strategy_type = None
    if strategy:
        if hasattr(strategy, 'monthly_amount'):
            strategy_type = 'fixed'
        elif hasattr(strategy, 'base_salary'):
            strategy_type = 'bonus'

    # Історія зарплат за 6 місяців
    salary_history = []
    current_date = date.today()

    for i in range(6):
        month_date = current_date.replace(day=1) - timedelta(days=i * 30)
        month_date = month_date.replace(day=1)

        month_name = month_date.strftime('%B %Y')

        # Базова зарплата
        if strategy_type == 'fixed':
            base = float(strategy.monthly_amount) if strategy else 0
            bonus_amount = 0
        elif strategy_type == 'bonus':
            base = float(strategy.base_salary) if strategy else 0
            bonus_amount = float(strategy.base_salary * strategy.bonus_percentage / 100) if strategy else 0
        else:
            base = 0
            bonus_amount = 0

        total = base + bonus_amount

        # Відпрацьовані години
        month_start = month_date
        if month_date.month == 12:
            month_end = month_date.replace(year=month_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_date.replace(month=month_date.month + 1, day=1) - timedelta(days=1)

        records = TimeRecord.objects.filter(
            employee=employee,
            date__gte=month_start,
            date__lte=month_end
        )

        hours_worked = sum([r.calculate_hours() for r in records])
        days_worked = records.values('date').distinct().count()

        salary_history.append({
            'month': month_name,
            'month_date': month_date,
            'base_salary': base,
            'bonus': bonus_amount,
            'total': total,
            'hours_worked': round(hours_worked, 1),
            'days_worked': days_worked,
        })

    unread_count = Notification.objects.filter(
        recipient=employee,
        is_read=False
    ).count()

    context = {
        'employee': employee,
        'current_salary': current_salary,
        'strategy': strategy,
        'strategy_type': strategy_type,
        'salary_history': salary_history,
        'unread_count': unread_count,
    }

    return render(request, 'employee/my_salary.html', context)
