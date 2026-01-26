from rest_framework import serializers
from .models import Employee, SalaryStrategy


class SalaryStrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryStrategy
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    salary = serializers.SerializerMethodField()
    salary_strategy_details = SalaryStrategySerializer(source='salary_strategy', read_only=True)

    class Meta:
        model = Employee
        fields = '__all__'

    def get_salary(self, obj):
        return obj.get_salary()