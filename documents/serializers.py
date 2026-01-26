from rest_framework import serializers
from .models import Contract, LeaveRequest


class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = '__all__'


class LeaveRequestSerializer(serializers.ModelSerializer):
    days_count = serializers.SerializerMethodField()

    class Meta:
        model = LeaveRequest
        fields = '__all__'

    def get_days_count(self, obj):
        if obj.start_date and obj.end_date:
            return (obj.end_date - obj.start_date).days + 1
        return 0
