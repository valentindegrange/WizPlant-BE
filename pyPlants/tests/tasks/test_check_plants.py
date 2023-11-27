from django.test import TestCase, tag
from freezegun import freeze_time

from pyPlants.constants import Seasons
from pyPlants.models import PlantUser, NotificationCenter, Notification, Plant
from pyPlants.tasks import check_plants


@tag('check-plants-task')
class CheckPlantTest(TestCase):
    def setUp(self):
        self.user = PlantUser.objects.create_user(
            email='foo@bar.com'
        )
        self.notification_center = NotificationCenter.objects.get(user=self.user)
        self.notification_center.preferred_notification_hour = 12
        self.notification_center.save()

        self.plant_only_water = Plant.objects.create(
            name='Pachira',
            user=self.user,
            water_frequency_summer=7,
            water_frequency_winter=14,
        )

        self.user_2 = PlantUser.objects.create_user(
            email='bar@bar.com'
        )
        self.notification_center_2 = NotificationCenter.objects.get(user=self.user_2)
        self.notification_center_2.preferred_notification_hour = 12
        self.notification_center_2.save()


    def test_check_plants_initial_run(self):
        self.assertEqual(Notification.objects.count(), 0)
        check_plants(self.user.id)
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.user)

    def test_check_plants_multiple_runs(self):
        self.assertEqual(Notification.objects.count(), 0)
        check_plants(self.user.id)
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.user)
        check_plants(self.user.id)
        self.assertEqual(Notification.objects.count(), 2)
        notification = Notification.objects.last()
        self.assertEqual(notification.user, self.user)
        check_plants(self.user.id)
        self.assertEqual(Notification.objects.count(), 3)
        notification = Notification.objects.last()
        self.assertEqual(notification.user, self.user)

    def test_check_plants_does_not_trigger_when_watered(self):
        self.plant_only_water.water()
        check_plants(self.user.id)
        self.assertEqual(Notification.objects.count(), 0)

    def test_check_plants_does_not_trigger_when_already_watered(self):
        with freeze_time('2023-01-01'):
            self.plant_only_water.water()
            check_plants(self.user.id)
            self.assertEqual(Notification.objects.count(), 0)
        with freeze_time('2023-01-02'):
            check_plants(self.user.id)
            self.assertEqual(Notification.objects.count(), 0)

    def test_check_plants_properly_triggers_in_the_future(self):
        with freeze_time('2023-01-01'):
            self.plant_only_water.water()
            check_plants(self.user.id)
            self.assertEqual(Notification.objects.count(), 0)
        with freeze_time('2023-02-01'):
            check_plants(self.user.id)
            self.assertEqual(Notification.objects.count(), 1)
            notification = Notification.objects.first()
            self.assertEqual(notification.user, self.user)

    @freeze_time('2023-01-01')
    def test_check_plants_when_repotting_only_needed(self):
        self.plant_only_water.repotting = True
        self.plant_only_water.repotting_season = Seasons.WINTER
        self.plant_only_water.save()
        check_plants(self.user.id)
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.user)

    @freeze_time('2023-01-01')
    def test_check_plants_when_fertilizing_only_needed(self):
        self.plant_only_water.fertilizer = True
        self.plant_only_water.fertilizer_season = Seasons.WINTER
        self.plant_only_water.save()
        check_plants(self.user.id)
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.user)
