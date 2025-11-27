from rest_framework import viewsets
from .models import Request, RequestState
from .serializers import RequestSerializer, RequestStateSerializer


class RequestStateViewSet(viewsets.ModelViewSet):
    queryset = RequestState.objects.all()
    serializer_class = RequestStateSerializer


class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer