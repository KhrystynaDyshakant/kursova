from rest_framework import viewsets
from .models import Employee, SalaryStrategy
from .serializers import EmployeeSerializer, SalaryStrategySerializer


class SalaryStrategyViewSet(viewsets.ModelViewSet):
    queryset = SalaryStrategy.objects.all()
    serializer_class = SalaryStrategySerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer