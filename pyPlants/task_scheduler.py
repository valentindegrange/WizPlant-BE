from django_celery_beat.models import PeriodicTask, CrontabSchedule


def schedule_check_plant_task(notification_center):
    user = notification_center.user
    schedule, _ = CrontabSchedule.objects.get_or_create(
        hour=notification_center.preferred_notification_hour,
        minute=0  # set to * for testing
    )
    task, _ = PeriodicTask.objects.get_or_create(
        name=f'Check plants for {user.email}',
        task='pyPlants.tasks.check_plants',
        crontab=schedule,
        args=[user.id]
    )
    return task
