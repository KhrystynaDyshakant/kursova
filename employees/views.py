from rest_framework import viewsets
from .models import Employee, SalaryStrategy
from .serializers import EmployeeSerializer, SalaryStrategySerializer
from rest_framework.permissions import AllowAny


class SalaryStrategyViewSet(viewsets.ModelViewSet):
    queryset = SalaryStrategy.objects.all()
    serializer_class = SalaryStrategySerializer
    permission_classes = [AllowAny]


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [AllowAny]