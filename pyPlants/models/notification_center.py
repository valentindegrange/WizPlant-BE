from django.db import models

from pyPlants.models import AbstractPlantModel, PlantUser
from pyPlants.task_scheduler import schedule_check_plant_task


class NotificationCenter(AbstractPlantModel):
    user = models.OneToOneField(PlantUser, on_delete=models.CASCADE)
    enable_in_app_notifications = models.BooleanField(default=True)
    enable_email_notifications = models.BooleanField(default=False)
    enable_sms_notifications = models.BooleanField(default=False)
    preferred_notification_hour = models.IntegerField(default=9)
    last_notification_sent = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        schedule_check_plant_task(self)
        super().save(*args, **kwargs)
