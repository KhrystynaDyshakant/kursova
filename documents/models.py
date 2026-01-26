from django.db import models
from abc import ABC, abstractmethod
from decimal import Decimal


class Document(ABC):
    """
    <<abstract>> Document
    Абстрактний базовий клас для документів (Factory Pattern)
    """

    @abstractmethod
    def generate(self):
        """Генерує документ"""
        pass

    @abstractmethod
    def approve(self):
        """Затверджує документ"""
        pass

    @abstractmethod
    def reject(self):
        """Відхиляє документ"""
        pass


class DocumentFactory(ABC):
    """
    <<abstract>> DocumentFactory
    Абстрактна фабрика для створення документів (Factory Pattern)
    """

    @abstractmethod
    def create_document(self, **kwargs):
        """Створює документ"""
        pass


# ============================================
# Contract - Контракт співробітника
# ============================================

class Contract(models.Model):
    """
    Contract - контракт співробітника
    Реалізує інтерфейс: Document
    """
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        verbose_name="Співробітник"
    )
    position = models.CharField(max_length=100, verbose_name="Посада")
    salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Зарплата")
    start_date = models.DateField(verbose_name="Дата початку")
    end_date = models.DateField(null=True, blank=True, verbose_name="Дата закінчення")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Очікує'), ('approved', 'Затверджено'), ('rejected', 'Відхилено')],
        default='pending',
        verbose_name="Статус"
    )

    class Meta:
        verbose_name = "Контракт"
        verbose_name_plural = "Контракти"

    def generate(self):
        return {
            'type': 'contract',
            'employee_id': self.employee_id,
            'position': self.position,
            'salary': str(self.salary),
            'start_date': str(self.start_date),
            'end_date': str(self.end_date) if self.end_date else None
        }

    def approve(self):
        self.status = 'approved'
        self.save()

    def reject(self):
        self.status = 'rejected'
        self.save()

    def __str__(self):
        return f"Контракт: {self.employee}"


Document.register(Contract)


class ContractFactory:
    """
    ContractFactory - фабрика для створення контрактів
    Реалізує інтерфейс: DocumentFactory
    """

    def create_document(self, employee, position, salary, start_date, end_date=None):
        contract = Contract.objects.create(
            employee=employee,
            position=position,
            salary=salary,
            start_date=start_date,
            end_date=end_date
        )
        contract.generate()
        return contract


DocumentFactory.register(ContractFactory)


# ============================================
# LeaveRequest - Заявка на відпустку
# ============================================

class LeaveRequest(models.Model):
    """
    LeaveRequest - заявка на відпустку
    Реалізує інтерфейс: Document
    """
    LEAVE_TYPES = [
        ('vacation', 'Відпустка'),
        ('sick', 'Лікарняний'),
    ]

    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        verbose_name="Співробітник"
    )
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES, verbose_name="Тип")
    reason = models.TextField(verbose_name="Причина")
    start_date = models.DateField(verbose_name="Дата початку")
    end_date = models.DateField(verbose_name="Дата закінчення")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Очікує'), ('approved', 'Затверджено'), ('rejected', 'Відхилено')],
        default='pending',
        verbose_name="Статус"
    )

    class Meta:
        verbose_name = "Заявка на відпустку"
        verbose_name_plural = "Заявки на відпустку"

    def generate(self):
        return {
            'type': 'leave_request',
            'employee_id': self.employee_id,
            'leave_type': self.leave_type,
            'reason': self.reason,
            'start_date': str(self.start_date),
            'end_date': str(self.end_date)
        }

    def approve(self):
        self.status = 'approved'
        self.save()

    def reject(self):
        self.status = 'rejected'
        self.save()

    def __str__(self):
        return f"{self.get_leave_type_display()} - {self.employee}"


Document.register(LeaveRequest)


class LeaveRequestFactory:
    """
    LeaveRequestFactory - фабрика для створення заявок на відпустку
    Реалізує інтерфейс: DocumentFactory
    """

    def create_document(self, employee, leave_type, reason, start_date, end_date):
        leave_request = LeaveRequest.objects.create(
            employee=employee,
            leave_type=leave_type,
            reason=reason,
            start_date=start_date,
            end_date=end_date
        )
        leave_request.generate()
        return leave_request


DocumentFactory.register(LeaveRequestFactory)


# ============================================
# Vacancy - Вакансія (Document)
# ============================================

class Vacancy(models.Model):
    """
    Vacancy - вакансія
    Реалізує інтерфейс: Document
    """
    title = models.CharField(max_length=200, verbose_name="Назва посади")
    department = models.CharField(max_length=100, verbose_name="Відділ")
    description = models.TextField(verbose_name="Опис вакансії")
    requirements = models.TextField(verbose_name="Вимоги")
    salary_from = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Зарплата від")
    salary_to = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Зарплата до")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Очікує'), ('approved', 'Затверджено'), ('rejected', 'Відхилено')],
        default='approved',
        verbose_name="Статус"
    )

    class Meta:
        verbose_name = "Вакансія"
        verbose_name_plural = "Вакансії"

    def generate(self):
        return {
            'type': 'vacancy',
            'title': self.title,
            'department': self.department,
            'description': self.description,
            'requirements': self.requirements,
            'salary_from': str(self.salary_from),
            'salary_to': str(self.salary_to)
        }

    def approve(self):
        self.status = 'approved'
        self.is_active = True
        self.save()

    def reject(self):
        self.status = 'rejected'
        self.is_active = False
        self.save()

    def candidates_count(self):
        return self.candidate_set.count()

    def __str__(self):
        return f"{self.title} ({self.department})"


Document.register(Vacancy)


class VacancyFactory:
    """
    VacancyFactory - фабрика для створення вакансій
    Реалізує інтерфейс: DocumentFactory
    """

    def create_document(self, title, department, description, requirements, salary_from, salary_to):
        vacancy = Vacancy.objects.create(
            title=title,
            department=department,
            description=description,
            requirements=requirements,
            salary_from=salary_from,
            salary_to=salary_to
        )
        vacancy.generate()
        return vacancy


DocumentFactory.register(VacancyFactory)


# ============================================
# Candidate - Кандидат на вакансію
# ============================================

class Candidate(models.Model):
    """
    Candidate - кандидат на вакансію
    Пов'язаний з Vacancy (1 вакансія - багато кандидатів)
    """
    STATUS_CHOICES = [
        ('new', 'Новий'),
        ('review', 'На розгляді'),
        ('interview', 'Співбесіда'),
        ('offer', 'Оффер'),
        ('hired', 'Прийнятий'),
        ('rejected', 'Відхилений'),
    ]

    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, verbose_name="Вакансія")
    first_name = models.CharField(max_length=100, verbose_name="Ім'я")
    last_name = models.CharField(max_length=100, verbose_name="Прізвище")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    resume = models.TextField(blank=True, verbose_name="Резюме")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    notes = models.TextField(blank=True, verbose_name="Нотатки HR")
    applied_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата подачі")

    class Meta:
        verbose_name = "Кандидат"
        verbose_name_plural = "Кандидати"

    def update_status(self, new_status):
        self.status = new_status
        self.save()

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.vacancy.title}"
