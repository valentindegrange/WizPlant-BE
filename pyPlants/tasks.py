from celery import shared_task
from django.contrib.auth.models import User

from pyPlants.models import Plant, NotificationCenter


@shared_task
def check_plants(user_id):
    user = User.objects.get(id=user_id)
    notification_center = NotificationCenter.objects.get(user=user)
    plants = Plant.objects.filter(user=user)

    actions = list()

    for plant in plants:
        action = dict(plant=plant.name, actions=list())
        if plant.should_water():
            action['actions'].append('water')
        if plant.should_fertilize():
            action['actions'].append('fertilize')
        if plant.should_repot():
            action['actions'].append('repot')

        if action['actions']:
            actions.append(action)

    if actions:
        # wrap this up based on the notification preferences
        message = f'Hey {user.username}, it seems you have some plants that need your attention! See below:\n'
        for action in actions:
            message += f'Your {action["plant"]} needs you to {", ".join(action["actions"])}.\n'
        notification_center.send_message(message)
