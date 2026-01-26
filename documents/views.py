from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Contract, LeaveRequest
from .serializers import ContractSerializer, LeaveRequestSerializer


class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [AllowAny]


class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [AllowAny]
