from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Request, PendingState, ApprovedState, RejectedState
from .serializers import RequestSerializer, PendingStateSerializer, ApprovedStateSerializer, RejectedStateSerializer


class PendingStateViewSet(viewsets.ModelViewSet):
    queryset = PendingState.objects.all()
    serializer_class = PendingStateSerializer
    permission_classes = [AllowAny]


class ApprovedStateViewSet(viewsets.ModelViewSet):
    queryset = ApprovedState.objects.all()
    serializer_class = ApprovedStateSerializer
    permission_classes = [AllowAny]


class RejectedStateViewSet(viewsets.ModelViewSet):
    queryset = RejectedState.objects.all()
    serializer_class = RejectedStateSerializer
    permission_classes = [AllowAny]


class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        req = self.get_object()
        req.approve()
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        req = self.get_object()
        req.reject()
        return Response({'status': 'rejected'})
