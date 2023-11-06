import logging

from celery import shared_task

from pyPlants.models import PlantUser, Plant, NotificationCenter
from pyPlants.notification_manager.service import NotificationManager
from pyPlants.data_classes.action_plant import ActionPlant

logger = logging.getLogger(__name__)


@shared_task
def check_plants(user_id):
    user = PlantUser.objects.get(id=user_id)
    notification_center = NotificationCenter.objects.get(user=user)
    plants = Plant.objects.filter(user=user)

    plant_action = ActionPlant()

    for plant in plants:
        if plant.should_water():
            plant_action.add_water(plant)
        if plant.should_fertilize():
            plant_action.add_fertilize(plant)
        if plant.should_repot():
            plant_action.add_repot(plant)

    if not plant_action.is_empty():
        notification_manager = NotificationManager(notification_center=notification_center, plant_action=plant_action)
        notifications = notification_manager.send_notifications()
        logger.info(f'{len(notifications)} Notifications sent!\nDetails:\n{notifications}')
