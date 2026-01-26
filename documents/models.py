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

    # Додайте ці моделі в кінець файлу documents/models.py

class Order(models.Model):
        """Накази (наприклад, наказ про відпустку)"""
        ORDER_TYPES = [
            ('vacation', 'Наказ про відпустку'),
            ('hire', 'Наказ про прийняття на роботу'),
            ('fire', 'Наказ про звільнення'),
            ('promotion', 'Наказ про підвищення'),
        ]

        order_type = models.CharField(max_length=20, choices=ORDER_TYPES, verbose_name="Тип наказу")
        employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, verbose_name="Співробітник")
        order_number = models.CharField(max_length=50, verbose_name="Номер наказу")
        order_date = models.DateField(verbose_name="Дата наказу")
        content = models.TextField(verbose_name="Зміст наказу")
        created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, verbose_name="Створив")

        def __str__(self):
            return f"Наказ №{self.order_number} - {self.get_order_type_display()}"

        class Meta:
            verbose_name = "Наказ"
            verbose_name_plural = "Накази"
            ordering = ['-order_date']

class Vacancy(models.Model):
        """Вакансії"""
        title = models.CharField(max_length=200, verbose_name="Назва вакансії")
        department = models.CharField(max_length=100, verbose_name="Відділ")
        description = models.TextField(verbose_name="Опис")
        requirements = models.TextField(verbose_name="Вимоги")
        salary_from = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Зарплата від")
        salary_to = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Зарплата до")
        is_active = models.BooleanField(default=True, verbose_name="Активна")
        created_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")

        def __str__(self):
            return self.title

        class Meta:
            verbose_name = "Вакансія"
            verbose_name_plural = "Вакансії"
            ordering = ['-created_date']

class Candidate(models.Model):
        """Кандидати"""
        STATUS_CHOICES = [
            ('new', 'Новий'),
            ('interview', 'На співбесіді'),
            ('offer', 'Оффер надіслано'),
            ('hired', 'Прийнято'),
            ('rejected', 'Відхилено'),
        ]

        vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, verbose_name="Вакансія")
        first_name = models.CharField(max_length=100, verbose_name="Ім'я")
        last_name = models.CharField(max_length=100, verbose_name="Прізвище")
        email = models.EmailField(verbose_name="Email")
        phone = models.CharField(max_length=20, verbose_name="Телефон")
        resume = models.TextField(verbose_name="Резюме/Досвід")
        status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
        notes = models.TextField(blank=True, verbose_name="Примітки HR")
        applied_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата подачі")

        def __str__(self):
            return f"{self.first_name} {self.last_name} - {self.vacancy.title}"

        class Meta:
            verbose_name = "Кандидат"
            verbose_name_plural = "Кандидати"
            ordering = ['-applied_date']


# ========== FACTORY METHOD PATTERN ==========

class DocumentFactory:
    """Абстрактна фабрика для створення документів (Factory Method Pattern)"""

    @staticmethod
    def create_document(document_type, **kwargs):
        """
        Фабричний метод для створення документів різних типів

        Args:
            document_type: тип документа ('contract' або 'leave_request')
            **kwargs: параметри для конкретного типу документа

        Returns:
            Об'єкт Contract або LeaveRequest
        """
        # Створюємо базовий документ
        document = Document.objects.create(
            document_type=document_type,
            status='pending'
        )

        # Викликаємо відповідну фабрику
        if document_type == 'contract':
            return ContractFactory.create_document(document, **kwargs)
        elif document_type == 'leave_request':
            return LeaveRequestFactory.create_document(document, **kwargs)
        else:
            raise ValueError(f"Невідомий тип документа: {document_type}")


class ContractFactory:
    """Фабрика для створення контрактів"""

    @staticmethod
    def create_document(document, employee, position, salary, start_date, end_date=None):
        """Створити контракт через Factory Pattern"""
        contract = Contract.objects.create(
            document=document,
            employee=employee,
            position=position,
            salary=salary,
            start_date=start_date,
            end_date=end_date
        )

        print(f"📄 [FACTORY PATTERN] Створено контракт для {employee.first_name} {employee.last_name}")

        return contract


class LeaveRequestFactory:
    """Фабрика для створення заявок на відпустку"""

    @staticmethod
    def create_document(document, employee, leave_type, reason, start_date, end_date):
        """Створити заявку на відпустку через Factory Pattern"""
        leave_request = LeaveRequest.objects.create(
            document=document,
            employee=employee,
            leave_type=leave_type,
            reason=reason,
            start_date=start_date,
            end_date=end_date
        )

        print(
            f"📋 [FACTORY PATTERN] Створено офіційний документ LeaveRequest для {employee.first_name} {employee.last_name}")
        print(f"    Тип: {leave_request.get_leave_type_display()}")
        print(f"    Період: {start_date} - {end_date}")

        return leave_request