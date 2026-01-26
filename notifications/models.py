from django.db import models


class Notification(models.Model):

    NOTIFICATION_TYPES = [
        ('system', 'Системне'),
        ('leave_approved', 'Відпустку схвалено'),
        ('leave_rejected', 'Відпустку відхилено'),
        ('request_created', 'Заявку створено'),
    ]

    CHANNEL_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push'),
    ]

    recipient = models.ForeignKey(
        'employees.Employee',
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

    class Meta:
        verbose_name = "Сповіщення"
        verbose_name_plural = "Сповіщення"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_notification_type_display()} для {self.recipient}"


class NotificationService:

    def __init__(self):
        self._observers = []

    @property
    def observers(self):
        return self._observers.copy()

    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, message):
        for observer in self._observers:
            observer.update(message)
