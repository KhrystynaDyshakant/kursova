from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required


@login_required
def redirect_after_login(request):
    """Перенаправлення після входу залежно від ролі"""
    user = request.user

    # Якщо HR - на панель HR
    if hasattr(user, 'role') and user.role == 'hr':
        return redirect('hr_dashboard')

    # Якщо суперюзер - на admin
    if user.is_superuser and not hasattr(user, 'role'):
        return redirect('/admin/')

    # Інакше - на панель співробітника
    return redirect('employee_dashboard')