from django.test import TestCase, tag
from django.core.management import call_command

from pyPlants.models import PlantUser, NotificationCenter, Plant
from pyPlants.management.commands.gen_db import USERS, PLANTS


@tag('gen-db')
class GenDbTest(TestCase):
    def test_gen_db(self):
        self.assertEqual(PlantUser.objects.count(), 0)
        self.assertEqual(Plant.objects.count(), 0)
        self.assertEqual(NotificationCenter.objects.count(), 0)
        call_command('gen_db')
        self.assertEqual(PlantUser.objects.count(), len(USERS))
        self.assertEqual(Plant.objects.count(), len(PLANTS) * len(USERS))
        self.assertEqual(NotificationCenter.objects.count(), len(USERS))
