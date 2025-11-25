from django.db import models
from employees.models import Employee


class Document(models.Model):
    """Абстрактний базовий клас для документів (Factory Pattern)"""
    DOCUMENT_TYPES = [
        ('contract', 'Контракт'),
        ('leave_request', 'Заявка на відпустку'),
    ]

    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Очікує'),
            ('approved', 'Затверджено'),
            ('rejected', 'Відхилено'),
        ],
        default='pending',
        verbose_name="Статус"
    )

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документи"

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.created_date.date()}"


class Contract(models.Model):
    """Контракт співробітника"""
    document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name='contract')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Співробітник")
    position = models.CharField(max_length=100, verbose_name="Посада")
    salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Зарплата")
    start_date = models.DateField(verbose_name="Дата початку")
    end_date = models.DateField(null=True, blank=True, verbose_name="Дата закінчення")

    def __str__(self):
        return f"Контракт {self.employee}"

    class Meta:
        verbose_name = "Контракт"
        verbose_name_plural = "Контракти"


class LeaveRequest(models.Model):
    """Заявка на відпустку/лікарняний"""
    LEAVE_TYPES = [
        ('vacation', 'Відпустка'),
        ('sick', 'Лікарняний'),
    ]

    document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name='leave_request')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Співробітник")
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES, verbose_name="Тип")
    reason = models.TextField(verbose_name="Причина")
    start_date = models.DateField(verbose_name="Дата початку")
    end_date = models.DateField(verbose_name="Дата закінчення")

    def __str__(self):
        return f"{self.get_leave_type_display()} - {self.employee}"

    class Meta:
        verbose_name = "Заявка на відпустку"
        verbose_name_plural = "Заявки на відпустку"