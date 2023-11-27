from django.core.management.base import BaseCommand
from django.db import transaction

from pyPlants.models import PlantUser, Plant, NotificationCenter
from logging import getLogger

logger = getLogger(__name__)

USERS = ['foo@bar.com', 'bar@bar.com']
PLANTS = ['Pachira', 'Croton', 'Pilea', 'Monstera', 'Ficus', 'Aloe']


class Command(BaseCommand):
    help = 'Generates a database with sample data'

    @transaction.atomic
    def handle(self, *args, **options):
        for user in USERS:
            logger.info(f'Creating user {user}')
            usr = PlantUser.objects.create_user(
                email=user, is_superuser=True, is_staff=True)
            usr.set_password('password')
            usr.save()
            nt_ct = NotificationCenter.objects.get(user=usr)
            nt_ct.enable_email_notifications = True
            nt_ct.enable_sms_notifications = False
            nt_ct.preferred_notification_hour = 9
            nt_ct.save()
            for plant in PLANTS:
                logger.info(f'Creating plant {plant}')
                Plant.objects.create(name=plant, user=usr, water_frequency_summer=7, water_frequency_winter=14)
        logger.info('Done!')
