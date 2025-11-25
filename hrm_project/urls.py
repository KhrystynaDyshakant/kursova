from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from employees.views import EmployeeViewSet, SalaryStrategyViewSet
from documents.views import DocumentViewSet, ContractViewSet, LeaveRequestViewSet
from requests.views import RequestViewSet, RequestStateViewSet
from notifications.views import NotificationViewSet
from timetracking.views import TimeRecordViewSet

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet)
router.register(r'salary-strategies', SalaryStrategyViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'contracts', ContractViewSet)
router.register(r'leave-requests', LeaveRequestViewSet)
router.register(r'requests', RequestViewSet)
router.register(r'request-states', RequestStateViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'time-records', TimeRecordViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]