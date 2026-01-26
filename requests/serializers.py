from rest_framework import serializers
from .models import Request, RequestState


class RequestStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestState
        fields = '__all__'


class RequestSerializer(serializers.ModelSerializer):
    state_details = RequestStateSerializer(source='current_state', read_only=True)

    class Meta:
        model = Request
        fields = '__all__'