from django.db import models
from django.utils import timezone

from pyPlants.constants import Notifications
from pyPlants.models import AbstractPlantModel, PlantUser


class NotificationType(models.TextChoices):
    EMAIL = Notifications.EMAIL, Notifications.EMAIL
    SMS = Notifications.SMS, Notifications.SMS
    IN_APP = Notifications.IN_APP, Notifications.IN_APP


class Notification(AbstractPlantModel):
    user = models.ForeignKey(PlantUser, on_delete=models.CASCADE)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.IN_APP,
    )
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    viewed = models.BooleanField(default=False)
    viewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.email} - {self.notification_type} - {self.message}'

    def mark_as_viewed(self):
        self.viewed = True
        self.viewed_at = timezone.now()
        self.save()

    def mark_as_sent(self):
        from pyPlants.models import NotificationCenter
        self.sent = True
        self.sent_at = timezone.now()
        self.save()
        NotificationCenter.objects.filter(user=self.user).update(last_notification_sent=timezone.now())
