from django.db import models
from employees.models import Employee


class RequestState(models.Model):
    """Стани заявок (State Pattern)"""
    STATE_TYPES = [
        ('pending', 'Очікує розгляду'),
        ('approved', 'Схвалено'),
        ('rejected', 'Відхилено'),
    ]

    state_type = models.CharField(
        max_length=20,
        choices=STATE_TYPES,
        unique=True,
        verbose_name="Тип стану"
    )

    def __str__(self):
        return self.get_state_type_display()

    class Meta:
        verbose_name = "Стан заявки"
        verbose_name_plural = "Стани заявок"


class Request(models.Model):
    """Заявки співробітників (відпустки, лікарняні тощо)"""
    REQUEST_TYPES = [
        ('vacation', 'Відпустка'),
        ('sick', 'Лікарняний'),
        ('remote', 'Віддалена робота'),
        ('other', 'Інше'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        verbose_name="Співробітник"
    )
    request_type = models.CharField(
        max_length=20,
        choices=REQUEST_TYPES,
        default='vacation',
        verbose_name="Тип заявки"
    )
    reason = models.TextField(
        blank=True,
        verbose_name="Причина/Опис"
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Дата початку"
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Дата завершення"
    )
    current_state = models.ForeignKey(
        RequestState,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Поточний стан"
    )
    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата створення"
    )
    hr_comment = models.TextField(
        blank=True,
        verbose_name="Коментар HR"
    )

    def change_state(self, new_state_type):
        """Змінити стан заявки (State Pattern)"""
        try:
            new_state = RequestState.objects.get(state_type=new_state_type)
            self.current_state = new_state
            self.save()
        except RequestState.DoesNotExist:
            pass

    def days_count(self):
        """Кількість днів"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

    def __str__(self):
        return f"Заявка #{self.id} - {self.employee.first_name} {self.employee.last_name}"

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ['-created_date']