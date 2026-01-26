from rest_framework import viewsets
from .models import Request, RequestState
from .serializers import RequestSerializer, RequestStateSerializer
from rest_framework.permissions import AllowAny


class RequestStateViewSet(viewsets.ModelViewSet):
    queryset = RequestState.objects.all()
    serializer_class = RequestStateSerializer
    permission_classes = [AllowAny]


class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [AllowAny]