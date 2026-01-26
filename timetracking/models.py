from django.db import models
from django.utils import timezone
from decimal import Decimal
import threading


class TimeRecord(models.Model):

    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        verbose_name="Співробітник"
    )
    clock_in_time = models.DateTimeField(verbose_name="Час входу")
    clock_out_time = models.DateTimeField(null=True, blank=True, verbose_name="Час виходу")
    date = models.DateField(verbose_name="Дата")

    class Meta:
        verbose_name = "Запис робочого часу"
        verbose_name_plural = "Записи робочого часу"
        ordering = ['-date', '-clock_in_time']

    def calculate_hours(self):
        if self.clock_out_time and self.clock_in_time:
            delta = self.clock_out_time - self.clock_in_time
            hours = Decimal(str(delta.total_seconds())) / Decimal('3600')
            return hours.quantize(Decimal('0.01'))
        return Decimal('0')

    def __str__(self):
        return f"{self.employee} - {self.date}"


class TimeTrackingSystem:

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        raise RuntimeError("Use TimeTrackingSystem.get_instance() instead")

    @classmethod
    def _create_instance(cls):
        instance = object.__new__(cls)
        instance._time_records = []
        return instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls._create_instance()
        return cls._instance

    @classmethod
    def reset_instance(cls):
        with cls._lock:
            cls._instance = None

    def clock_in(self, employee):
        now = timezone.now()
        today = now.date()

        existing = TimeRecord.objects.filter(
            employee=employee,
            date=today,
            clock_out_time__isnull=True
        ).first()

        if existing:
            return existing

        record = TimeRecord.objects.create(
            employee=employee,
            clock_in_time=now,
            date=today
        )
        return record

    def clock_out(self, employee):
        today = timezone.now().date()
        record = TimeRecord.objects.filter(
            employee=employee,
            date=today,
            clock_out_time__isnull=True
        ).first()

        if record:
            record.clock_out_time = timezone.now()
            record.save()
            return record
        return None

    def get_hours_worked(self, employee, target_date=None):
        if target_date is None:
            target_date = timezone.now().date()

        records = TimeRecord.objects.filter(
            employee=employee,
            date=target_date
        )

        total = Decimal('0')
        for record in records:
            total += record.calculate_hours()
        return total

    def get_work_history(self, employee):
        return list(TimeRecord.objects.filter(employee=employee).order_by('-date'))
