from rest_framework import viewsets
from .models import TimeRecord
from .serializers import TimeRecordSerializer
from rest_framework.permissions import AllowAny


class TimeRecordViewSet(viewsets.ModelViewSet):
    queryset = TimeRecord.objects.all()
    serializer_class = TimeRecordSerializer
    permission_classes = [AllowAny]