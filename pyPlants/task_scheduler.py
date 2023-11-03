from django_celery_beat.models import PeriodicTask, CrontabSchedule
from django.contrib.auth.models import User

from pyPlants.models import NotificationCenter


def schedule_check_plant_tasks():
    for user in User.objects.all():
        notification_center = NotificationCenter.objects.get(user=user)

        schedule, created = CrontabSchedule.objects.get_or_create(
            hour=notification_center.preferred_notification_hour,
            minute=0  # set to * for testing
        )

        task, created = PeriodicTask.objects.get_or_create(
            name=f'Check plants for {user.username}',
            task='pyPlants.tasks.check_plants',
            crontab=schedule,
            args=[user.id]
        )
