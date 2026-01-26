from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Розширена модель користувача"""
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
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Телефон"
    )
    email_notifications = models.BooleanField(
        default=True,
        verbose_name="Email сповіщення"
    )
    sms_notifications = models.BooleanField(
        default=False,
        verbose_name="SMS сповіщення"
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    class Meta:
        verbose_name = "Користувач"
        verbose_name_plural = "Користувачі"


class HR(models.Model):
    """HR менеджер"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='hr_profile'
    )
    managed_departments = models.JSONField(
        default=list,
        verbose_name="Керовані відділи"
    )

    def __str__(self):
        return f"HR: {self.user.username}"

    class Meta:
        verbose_name = "HR менеджер"
        verbose_name_plural = "HR менеджери"