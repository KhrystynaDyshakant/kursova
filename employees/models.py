from django.db import models


class SalaryStrategy(models.Model):
    """Абстрактна стратегія для розрахунку зарплати"""
    STRATEGY_TYPES = [
        ('fixed', 'Фіксована'),
        ('bonus', 'З бонусами'),
    ]

    strategy_type = models.CharField(max_length=20, choices=STRATEGY_TYPES)

    # Для фіксованої зарплати
    monthly_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Для зарплати з бонусами
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bonus_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def calculate_salary(self, employee):
        """Розрахунок зарплати (Strategy Pattern)"""
        if self.strategy_type == 'fixed':
            return self.monthly_amount
        elif self.strategy_type == 'bonus':
            return self.base_salary + (self.base_salary * self.bonus_percentage / 100)
        return 0

    def __str__(self):
        return f"{self.get_strategy_type_display()}"

    class Meta:
        verbose_name = "Стратегія зарплати"
        verbose_name_plural = "Стратегії зарплати"


class Employee(models.Model):
    """Модель співробітника"""
    first_name = models.CharField(max_length=100, verbose_name="Ім'я")
    last_name = models.CharField(max_length=100, verbose_name="Прізвище")
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    position = models.CharField(max_length=100, verbose_name="Посада")
    department = models.CharField(max_length=100, verbose_name="Відділ")
    hire_date = models.DateField(verbose_name="Дата найму")

    # Strategy Pattern - стратегія розрахунку зарплати
    salary_strategy = models.ForeignKey(
        SalaryStrategy,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Стратегія зарплати"
    )

    def get_salary(self):
        """Отримати зарплату згідно стратегії"""
        if self.salary_strategy:
            return self.salary_strategy.calculate_salary(self)
        return 0

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Співробітник"
        verbose_name_plural = "Співробітники"