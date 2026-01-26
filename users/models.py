from django.db import models
from django.contrib.auth.models import AbstractUser
from employees.models import Observer


class User(AbstractUser):

    ROLE_CHOICES = [
        ('employee', 'Співробітник'),
        ('hr', 'HR'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='employee',
        verbose_name="Роль"
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    email_notifications = models.BooleanField(default=True, verbose_name="Email сповіщення")
    sms_notifications = models.BooleanField(default=False, verbose_name="SMS сповіщення")

    class Meta:
        verbose_name = "Користувач"
        verbose_name_plural = "Користувачі"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class HR(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='hr_profile'
    )
    name = models.CharField(max_length=100, verbose_name="Ім'я")
    email = models.EmailField(verbose_name="Email")
    managed_departments = models.JSONField(default=list, verbose_name="Керовані відділи")

    class Meta:
        verbose_name = "HR менеджер"
        verbose_name_plural = "HR менеджери"

    def update(self, message):
        from notifications.models import Notification
        from employees.models import Employee

        employee = Employee.objects.filter(email=self.email).first()
        if employee:
            Notification.objects.create(
                recipient=employee,
                notification_type='system',
                message=message,
                is_sent=True
            )

    def add_employee(self, employee):
        pass

    def remove_employee(self, employee):
        pass

    def process_request(self, request, approve=True):
        from requests.models import ApprovedState, RejectedState

        if approve:
            approved_state, _ = ApprovedState.objects.get_or_create(pk=1)
            request.change_state(approved_state)
        else:
            rejected_state, _ = RejectedState.objects.get_or_create(pk=1)
            request.change_state(rejected_state)

    def __str__(self):
        return f"HR: {self.name}"


Observer.register(HR)
