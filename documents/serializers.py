from rest_framework import serializers
from .models import Document, Contract, LeaveRequest


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'


class ContractSerializer(serializers.ModelSerializer):
    document_details = DocumentSerializer(source='document', read_only=True)

    class Meta:
        model = Contract
        fields = '__all__'


class LeaveRequestSerializer(serializers.ModelSerializer):
    document_details = DocumentSerializer(source='document', read_only=True)

    class Meta:
        model = LeaveRequest
        fields = '__all__'