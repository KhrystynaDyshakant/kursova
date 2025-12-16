from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# API ViewSets
from employees.views import EmployeeViewSet, SalaryStrategyViewSet
from documents.views import DocumentViewSet, ContractViewSet, LeaveRequestViewSet
from requests.views import RequestViewSet, RequestStateViewSet
from notifications.views import NotificationViewSet
from timetracking.views import TimeRecordViewSet

# Employee Views
from employees.employee_views import (
    employee_dashboard,
    clock_in,
    clock_out,
    submit_request,
    my_requests,
    request_detail,
    notifications_view,
    mark_as_read,
    my_salary,
)

# HR Views
from employees.hr_views import (
    hr_dashboard,
    pending_requests,
    approve_request,
    reject_request,
    all_employees,
    employee_detail,
    reports,
)

# Login redirect
from employees.login_views import redirect_after_login

# ========== API ROUTER ==========
router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'salary-strategies', SalaryStrategyViewSet, basename='salarystrategy')
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'contracts', ContractViewSet, basename='contract')
router.register(r'leave-requests', LeaveRequestViewSet, basename='leaverequest')
router.register(r'requests', RequestViewSet, basename='request')
router.register(r'request-states', RequestStateViewSet, basename='requeststate')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'time-records', TimeRecordViewSet, basename='timerecord')

# ========== SWAGGER/OPENAPI DOCUMENTATION ==========
schema_view = get_schema_view(
    openapi.Info(
        title="HRM System API",
        default_version='v1',
        description="REST API документація для HRM System",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="admin@hrm.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# ========== URL PATTERNS ==========
urlpatterns = [
    # ===== ADMIN =====
    path('admin/', admin.site.urls),

    # ===== API ENDPOINTS =====
    path('api/', include(router.urls)),

    # ===== API DOCUMENTATION =====
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),

    # ===== AUTHENTICATION =====
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/', http_method_names=['get', 'post']),
         name='logout'),
    path('accounts/profile/', redirect_after_login, name='profile_redirect'),

    # ===== EMPLOYEE URLS =====
    path('', employee_dashboard, name='employee_dashboard'),
    path('clock-in/', clock_in, name='clock_in'),
    path('clock-out/', clock_out, name='clock_out'),
    path('submit-request/', submit_request, name='submit_request'),
    path('my-requests/', my_requests, name='my_requests'),
    path('my-requests/<int:request_id>/', request_detail, name='request_detail'),
    path('my-salary/', my_salary, name='my_salary'),
    path('notifications/', notifications_view, name='notifications'),
    path('notifications/<int:notification_id>/read/', mark_as_read, name='mark_as_read'),

    # ===== HR URLS =====
    path('hr/', hr_dashboard, name='hr_dashboard'),
    path('hr/pending/', pending_requests, name='pending_requests'),
    path('hr/request/<int:request_id>/approve/', approve_request, name='approve_request'),
    path('hr/request/<int:request_id>/reject/', reject_request, name='reject_request'),
    path('hr/employees/', all_employees, name='all_employees'),
    path('hr/employee/<int:employee_id>/', employee_detail, name='employee_detail'),
    path('hr/reports/', reports, name='reports'),
]