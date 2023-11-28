from django_celery_beat.models import PeriodicTask, CrontabSchedule


def schedule_check_plant_task(notification_center):
    """
    Schedule a task to check the plants of a user
    """
    user = notification_center.user
    schedule, _ = CrontabSchedule.objects.get_or_create(
        hour=notification_center.preferred_notification_hour,
        minute=0  # set to * for testing
    )
    task, _ = PeriodicTask.objects.update_or_create(
        # name is used to identify the task and query it later
        name=f'Check plants for {user.email}',
        defaults=dict(
            task='pyPlants.tasks.check_plants',
            crontab=schedule,
            args=[user.id]
        )
    )
    return task
