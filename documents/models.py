from django.db import models
from abc import ABC, abstractmethod

class Document(ABC):

    @abstractmethod
    def generate(self):
        pass

    @abstractmethod
    def approve(self):
        pass

    @abstractmethod
    def reject(self):
        pass

class DocumentFactory(ABC):

    document_type = "base"
    auto_generate = True

    def log_creation(self, document):
        print(f"[FACTORY] Створено {self.document_type}: #{document.id}")
        return True

    def validate_before_create(self, **kwargs):
        if not kwargs:
            raise ValueError("Потрібні дані для створення документа")
        return True

    def get_document_type(self):
        return self.document_type

    @abstractmethod
    def create_document(self, **kwargs):
        pass

class Contract(models.Model):

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

class ContractFactory(DocumentFactory):

    document_type = "contract"

    def create_document(self, employee, position, salary, start_date, end_date=None):
        self.validate_before_create(employee=employee, position=position, salary=salary)

        contract = Contract.objects.create(
            employee=employee,
            position=position,
            salary=salary,
            start_date=start_date,
            end_date=end_date
        )

        if self.auto_generate:
            contract.generate()

        self.log_creation(contract)
        return contract

class LeaveRequest(models.Model):

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


class LeaveRequestFactory(DocumentFactory):

    document_type = "leave_request"

    def create_document(self, employee, leave_type, reason, start_date, end_date):
        self.validate_before_create(employee=employee, leave_type=leave_type)

        leave_request = LeaveRequest.objects.create(
            employee=employee,
            leave_type=leave_type,
            reason=reason,
            start_date=start_date,
            end_date=end_date
        )

        if self.auto_generate:
            leave_request.generate()

        self.log_creation(leave_request)
        return leave_request


class Vacancy(models.Model):

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

class VacancyFactory(DocumentFactory):

    document_type = "vacancy"

    def create_document(self, title, department, description, requirements, salary_from, salary_to):
        self.validate_before_create(title=title, department=department)

        vacancy = Vacancy.objects.create(
            title=title,
            department=department,
            description=description,
            requirements=requirements,
            salary_from=salary_from,
            salary_to=salary_to
        )

        if self.auto_generate:
            vacancy.generate()

        self.log_creation(vacancy)
        return vacancy

class Candidate(models.Model):

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
