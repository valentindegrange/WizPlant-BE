from celery import shared_task

from pyPlants.models import PlantUser, Plant, NotificationCenter


@shared_task
def check_plants(user_id):
    user = PlantUser.objects.get(id=user_id)
    notification_center = NotificationCenter.objects.get(user=user)
    plants = Plant.objects.filter(user=user)

    actions = dict(
        water=list(),
        repot=list(),
        fertilize=list(),
    )

    for plant in plants:
        if plant.should_water():
            actions['water'].append(plant.name)
        if plant.should_fertilize():
            actions['fertilize'].append(plant.name)
        if plant.should_repot():
            actions['repot'].append(plant.name)

    if actions['water'] or actions['fertilize'] or actions['repot']:
        # wrap this up based on the notification preferences
        message = f'Hey {user.email}, it seems you have some plants that need your attention! See below:\n'
        for key, values in actions.items():
            if values:
                message += f'You need to {key}: {", ".join(values)}.\n'
        notification_center.send_notification(message)
