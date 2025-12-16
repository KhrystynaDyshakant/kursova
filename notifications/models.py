from django.db import models
from employees.models import Employee


class Notification(models.Model):
    """Сповіщення (Observer Pattern)"""
    NOTIFICATION_TYPES = [
        ('order_created', 'Створено замовлення'),
        ('order_status', 'Зміна статусу замовлення'),
        ('leave_approved', 'Відпустку схвалено'),
        ('leave_rejected', 'Відпустку відхилено'),
    ]

    CHANNEL_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push'),
    ]

    recipient = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        verbose_name="Одержувач"
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPES,
        verbose_name="Тип сповіщення"
    )
    channel = models.CharField(
        max_length=20,
        choices=CHANNEL_TYPES,
        default='push',
        verbose_name="Канал"
    )
    message = models.TextField(verbose_name="Повідомлення")
    is_sent = models.BooleanField(default=False, verbose_name="Надіслано")
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")

    def __str__(self):
        return f"{self.get_notification_type_display()} для {self.recipient}"

    class Meta:
        verbose_name = "Сповіщення"
        verbose_name_plural = "Сповіщення"
        ordering = ['-created_at']


class NotificationService:
    """Сервіс для відправки сповіщень (Observer Pattern - Subject)"""

    @staticmethod
    def notify(employee, notification_type, message, channels=['push']):
        """Створити та надіслати сповіщення"""
        notifications = []
        for channel in channels:
            notification = Notification.objects.create(
                recipient=employee,
                notification_type=notification_type,
                channel=channel,
                message=message,
                is_sent=True,
                is_read=False  # ← ДОДАНО!
            )
            notifications.append(notification)
        return notifications