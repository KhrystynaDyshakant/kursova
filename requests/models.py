from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from abc import ABC, abstractmethod


class RequestState(ABC):
    """
    <<interface>> RequestState
    Абстрактний базовий клас для станів заявки (State Pattern)
    """

    @abstractmethod
    def handle(self, request):
        pass


class PendingState(models.Model):
    """
    PendingState - стан "Очікує розгляду"
    Реалізує інтерфейс: RequestState
    """

    class Meta:
        verbose_name = "Стан: Очікує"
        verbose_name_plural = "Стани: Очікують"

    def handle(self, request):
        return {
            'status': 'pending',
            'message': f'Заявка #{request.id} очікує розгляду',
            'actions': ['approve', 'reject']
        }

    def __str__(self):
        return "Очікує розгляду"


RequestState.register(PendingState)


class ApprovedState(models.Model):
    """
    ApprovedState - стан "Схвалено"
    Реалізує інтерфейс: RequestState
    """

    class Meta:
        verbose_name = "Стан: Схвалено"
        verbose_name_plural = "Стани: Схвалені"

    def handle(self, request):
        return {
            'status': 'approved',
            'message': f'Заявка #{request.id} схвалена',
            'actions': []
        }

    def __str__(self):
        return "Схвалено"


RequestState.register(ApprovedState)


class RejectedState(models.Model):
    """
    RejectedState - стан "Відхилено"
    Реалізує інтерфейс: RequestState
    """

    class Meta:
        verbose_name = "Стан: Відхилено"
        verbose_name_plural = "Стани: Відхилені"

    def handle(self, request):
        return {
            'status': 'rejected',
            'message': f'Заявка #{request.id} відхилена',
            'actions': []
        }

    def __str__(self):
        return "Відхилено"


RequestState.register(RejectedState)


class Request(models.Model):
    """
    Request - заявка співробітника
    Використовує State Pattern для керування станами
    """
    REQUEST_TYPES = [
        ('vacation', 'Відпустка'),
        ('sick', 'Лікарняний'),
        ('remote', 'Віддалена робота'),
        ('other', 'Інше'),
    ]

    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        verbose_name="Співробітник"
    )
    request_type = models.CharField(
        max_length=20,
        choices=REQUEST_TYPES,
        default='vacation',
        verbose_name="Тип заявки"
    )
    reason = models.TextField(blank=True, verbose_name="Причина")
    start_date = models.DateField(null=True, blank=True, verbose_name="Дата початку")
    end_date = models.DateField(null=True, blank=True, verbose_name="Дата закінчення")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    hr_comment = models.TextField(blank=True, verbose_name="Коментар HR")

    current_state_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Тип стану"
    )
    current_state_id = models.PositiveIntegerField(null=True, blank=True)
    current_state = GenericForeignKey('current_state_type', 'current_state_id')

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ['-created_date']

    def change_state(self, new_state):
        self.current_state_type = ContentType.objects.get_for_model(new_state)
        self.current_state_id = new_state.id
        self.save()

    def process(self):
        if self.current_state:
            return self.current_state.handle(self)
        return None

    def approve(self):
        approved_state, _ = ApprovedState.objects.get_or_create(pk=1)
        self.change_state(approved_state)

    def reject(self):
        rejected_state, _ = RejectedState.objects.get_or_create(pk=1)
        self.change_state(rejected_state)

    def days_count(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

    def __str__(self):
        return f"Заявка #{self.id} - {self.employee}"
