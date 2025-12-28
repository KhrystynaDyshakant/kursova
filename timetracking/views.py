from rest_framework import viewsets
from .models import TimeRecord
from .serializers import TimeRecordSerializer


class TimeRecordViewSet(viewsets.ModelViewSet):
    queryset = TimeRecord.objects.all()
    serializer_class = TimeRecordSerializer