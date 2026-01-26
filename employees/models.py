from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from abc import ABC, abstractmethod
from decimal import Decimal


class SalaryStrategy(ABC):

    @abstractmethod
    def calculate_salary(self, employee):
        pass

    @abstractmethod
    def calculate_bonus(self, employee):
        pass


class Observer(ABC):

    @abstractmethod
    def update(self, message):
        pass


class FixedSalaryStrategy(models.Model):

    monthly_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Місячна сума"
    )

    class Meta:
        verbose_name = "Стратегія: Фіксована"
        verbose_name_plural = "Стратегії: Фіксовані"

    def calculate_salary(self, employee):
        return self.monthly_amount

    def calculate_bonus(self, employee):
        return Decimal('0')

    def __str__(self):
        return f"Фіксована: {self.monthly_amount} грн"


SalaryStrategy.register(FixedSalaryStrategy)


class BonusSalaryStrategy(models.Model):

    base_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Базова зарплата"
    )
    bonus_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Відсоток бонусу"
    )

    class Meta:
        verbose_name = "Стратегія: З бонусами"
        verbose_name_plural = "Стратегії: З бонусами"

    def calculate_salary(self, employee):
        bonus = self.calculate_bonus(employee)
        return self.base_salary + bonus

    def calculate_bonus(self, employee):
        return (self.base_salary * self.bonus_percentage / Decimal('100')).quantize(Decimal('0.01'))

    def __str__(self):
        return f"З бонусом: {self.base_salary} грн + {self.bonus_percentage}%"


SalaryStrategy.register(BonusSalaryStrategy)


class Employee(models.Model):

    first_name = models.CharField(max_length=100, verbose_name="Ім'я")
    last_name = models.CharField(max_length=100, verbose_name="Прізвище")
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    position = models.CharField(max_length=100, verbose_name="Посада")
    department = models.CharField(max_length=100, verbose_name="Відділ")
    hire_date = models.DateField(verbose_name="Дата найму")

    salary_strategy_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Тип стратегії"
    )
    salary_strategy_id = models.PositiveIntegerField(null=True, blank=True)
    salary_strategy = GenericForeignKey('salary_strategy_type', 'salary_strategy_id')

    class Meta:
        verbose_name = "Співробітник"
        verbose_name_plural = "Співробітники"

    def get_salary(self):
        if self.salary_strategy:
            return self.salary_strategy.calculate_salary(self)
        return Decimal('0')

    def get_bonus(self):
        if self.salary_strategy:
            return self.salary_strategy.calculate_bonus(self)
        return Decimal('0')

    def set_salary_strategy(self, strategy):
        self.salary_strategy_type = ContentType.objects.get_for_model(strategy)
        self.salary_strategy_id = strategy.id
        self.save()

    def submit_leave_request(self):
        from requests.models import Request, PendingState
        pending_state, _ = PendingState.objects.get_or_create(pk=1)
        request = Request.objects.create(
            employee=self,
            current_state=pending_state
        )
        return request

    def update(self, message):
        from notifications.models import Notification
        Notification.objects.create(
            recipient=self,
            notification_type='system',
            message=message,
            is_sent=True
        )

    def clock_in(self):
        from timetracking.models import TimeTrackingSystem
        TimeTrackingSystem.get_instance().clock_in(self)

    def clock_out(self):
        from timetracking.models import TimeTrackingSystem
        TimeTrackingSystem.get_instance().clock_out(self)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


Observer.register(Employee)
