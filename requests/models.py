from django.db import models
from employees.models import Employee


class RequestState(models.Model):
    """Стан заявки (State Pattern)"""
    STATE_TYPES = [
        ('pending', 'Очікує подання'),
        ('approved', 'Затверджено'),
        ('rejected', 'Відхилено'),
    ]

    state_type = models.CharField(max_length=20, choices=STATE_TYPES)

    def __str__(self):
        return self.get_state_type_display()

    class Meta:
        verbose_name = "Стан заявки"
        verbose_name_plural = "Стани заявок"


class Request(models.Model):
    """Заявка з можливістю зміни стану (State Pattern)"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Співробітник")
    current_state = models.ForeignKey(
        RequestState,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Поточний стан"
    )
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")

    def change_state(self, new_state_type):
        """Зміна стану заявки"""
        new_state, created = RequestState.objects.get_or_create(state_type=new_state_type)
        self.current_state = new_state
        self.save()

    def __str__(self):
        return f"Заявка #{self.id} - {self.employee}"

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"