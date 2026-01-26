from rest_framework import serializers
from .models import TimeRecord


class TimeRecordSerializer(serializers.ModelSerializer):
    hours_worked = serializers.SerializerMethodField()

    class Meta:
        model = TimeRecord
        fields = '__all__'

    def get_hours_worked(self, obj):
        return obj.calculate_hours()