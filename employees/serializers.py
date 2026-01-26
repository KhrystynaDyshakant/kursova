from rest_framework import serializers
from .models import Employee, FixedSalaryStrategy, BonusSalaryStrategy


class FixedSalaryStrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = FixedSalaryStrategy
        fields = '__all__'


class BonusSalaryStrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = BonusSalaryStrategy
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    salary = serializers.SerializerMethodField()
    bonus = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = '__all__'

    def get_salary(self, obj):
        return obj.get_salary()

    def get_bonus(self, obj):
        return obj.get_bonus()
