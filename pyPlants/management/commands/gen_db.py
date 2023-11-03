from django.core.management.base import BaseCommand
from django.db import transaction

from pyPlants.models import PlantUser, Plant, NotificationCenter
from logging import getLogger

logger = getLogger(__name__)


class Command(BaseCommand):
    help = 'Generates a database with sample data'

    @transaction.atomic
    def handle(self, *args, **options):
        users = ['foo@bar.com']
        for user in users:
            logger.info(f'Creating user {user}')
            usr = PlantUser.objects.create_user(
                email=user, is_superuser=True, is_staff=True)
            usr.set_password('password')
            usr.save()
            NotificationCenter.objects.create(
                user=usr,
                enable_email_notifications=True, enable_sms_notifications=False, preferred_notification_hour=9)
            plants = ['Pachira', 'Croton', 'Pilea', 'Monstera', 'Ficus', 'Aloe']
            for plant in plants:
                logger.info(f'Creating plant {plant}')
                Plant.objects.create(name=plant, user=usr, water_frequency_summer=7, water_frequency_winter=14)
        logger.info('Done!')
