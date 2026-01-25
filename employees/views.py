from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Employee, FixedSalaryStrategy, BonusSalaryStrategy
from .serializers import EmployeeSerializer, FixedSalaryStrategySerializer, BonusSalaryStrategySerializer


class FixedSalaryStrategyViewSet(viewsets.ModelViewSet):
    queryset = FixedSalaryStrategy.objects.all()
    serializer_class = FixedSalaryStrategySerializer
    permission_classes = [AllowAny]


class BonusSalaryStrategyViewSet(viewsets.ModelViewSet):
    queryset = BonusSalaryStrategy.objects.all()
    serializer_class = BonusSalaryStrategySerializer
    permission_classes = [AllowAny]


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [AllowAny]
