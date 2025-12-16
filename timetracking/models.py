from django.db import models
from employees.models import Employee
from datetime import datetime
from django.utils import timezone


class TimeRecord(models.Model):
    """Запис робочого часу"""
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        verbose_name="Співробітник"
    )
    clock_in_time = models.DateTimeField(verbose_name="Час входу")
    clock_out_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Час виходу"
    )
    date = models.DateField(verbose_name="Дата")

    def calculate_hours(self):
        """Розрахувати відпрацьовані години"""
        if self.clock_out_time and self.clock_in_time:
            # Переконатися що обидва datetime мають timezone
            clock_in = self.clock_in_time
            clock_out = self.clock_out_time

            # Якщо один має timezone, а інший ні - додати timezone
            if timezone.is_aware(clock_in) and timezone.is_naive(clock_out):
                clock_out = timezone.make_aware(clock_out)
            elif timezone.is_naive(clock_in) and timezone.is_aware(clock_out):
                clock_in = timezone.make_aware(clock_in)

            delta = clock_out - clock_in
            return round(delta.total_seconds() / 3600, 2)
        return 0

    def __str__(self):
        return f"{self.employee} - {self.date}"

    class Meta:
        verbose_name = "Запис робочого часу"
        verbose_name_plural = "Записи робочого часу"
        ordering = ['-date', '-clock_in_time']


class TimeTrackingSystem:
    """Singleton для системи обліку часу"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def clock_in(employee):
        """Зареєструвати вхід"""
        now = timezone.now()  # Використовуємо timezone-aware datetime
        record = TimeRecord.objects.create(
            employee=employee,
            clock_in_time=now,
            date=now.date()
        )
        return record

    @staticmethod
    def clock_out(employee):
        """Зареєструвати вихід"""
        today = timezone.now().date()
        try:
            record = TimeRecord.objects.filter(
                employee=employee,
                date=today,
                clock_out_time__isnull=True
            ).latest('clock_in_time')

            record.clock_out_time = timezone.now()  # Використовуємо timezone-aware datetime
            record.save()
            return record
        except TimeRecord.DoesNotExist:
            return None

    @staticmethod
    def get_hours_worked(employee, date=None):
        """Отримати відпрацьовані години"""
        if date is None:
            date = timezone.now().date()

        records = TimeRecord.objects.filter(
            employee=employee,
            date=date
        )

        total_hours = sum([record.calculate_hours() for record in records])
        return round(total_hours, 2)

    @staticmethod
    def get_work_history(employee):
        """Отримати історію роботи"""
        return TimeRecord.objects.filter(employee=employee)