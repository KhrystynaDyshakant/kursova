from rest_framework import serializers
from .models import Request, PendingState, ApprovedState, RejectedState


class PendingStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PendingState
        fields = '__all__'


class ApprovedStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovedState
        fields = '__all__'


class RejectedStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RejectedState
        fields = '__all__'


class RequestSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    days_count = serializers.SerializerMethodField()

    class Meta:
        model = Request
        fields = '__all__'

    def get_status(self, obj):
        result = obj.process()
        if result:
            return result.get('status')
        return None

    def get_days_count(self, obj):
        return obj.days_count()
