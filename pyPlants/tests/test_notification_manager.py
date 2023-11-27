from django.test import TestCase, tag

from pyPlants.constants import Seasons, Notifications
from pyPlants.data_classes.action_plant import ActionPlant
from pyPlants.models import PlantUser, Plant, NotificationCenter, Notification
from pyPlants.notification_manager.service import NotificationManager


@tag('notification-manager')
class NotificationManagerTest(TestCase):
    def setUp(self):
        self.user = PlantUser.objects.create_user(
            email='foo@bar.com'
        )
        self.notification_center = NotificationCenter.objects.get(user=self.user)
        self.notification_center.preferred_notification_hour = 12
        self.notification_center.enable_in_app_notifications = True
        self.notification_center.save()

        self.plant_1 = Plant.objects.create(
            name='Pachira',
            user=self.user,
            water_frequency_summer=7,
            water_frequency_winter=14,
        )
        self.plant_2 = Plant.objects.create(
            name='Tea Tree',
            user=self.user,
            water_frequency_summer=7,
            water_frequency_winter=14,
            repotting=True,
            repotting_season=Seasons.SPRING,
        )
        self.action_plant = ActionPlant()

    def test_base_init(self):
        notification_manager = NotificationManager(notification_center=self.notification_center,
                                                   plant_action=self.action_plant)
        self.assertEqual(notification_manager.notification_center, self.notification_center)
        self.assertEqual(notification_manager.plant_action, self.action_plant)
        self.assertTrue(notification_manager.should_send_in_app_notification)
        self.assertFalse(notification_manager.should_send_email_notification)
        self.assertFalse(notification_manager.should_send_sms_notification)
        notifications = notification_manager.send_notifications()
        self.assertListEqual(notifications, [])
        self.assertEqual(Notification.objects.count(), 0)

    def test_base_send_notifications(self):
        self.action_plant.add_water(self.plant_1)
        self.action_plant.add_repot(self.plant_1)
        self.action_plant.add_repot(self.plant_2)
        notification_manager = NotificationManager(notification_center=self.notification_center,
                                                   plant_action=self.action_plant)
        notifications = notification_manager.send_notifications()
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(len(notifications), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.user)
        self.assertListEqual(notifications, [notification])
        self.assertEqual(notification.notification_type, Notifications.IN_APP)
        self.assertTrue(notification.sent)

    def test_send_multi_notifications(self):
        self.action_plant.add_water(self.plant_1)
        self.notification_center.enable_email_notifications = True
        self.notification_center.enable_sms_notifications = True
        self.notification_center.save()
        notification_manager = NotificationManager(notification_center=self.notification_center,
                                                   plant_action=self.action_plant)
        notifications = notification_manager.send_notifications()
        self.assertEqual(Notification.objects.count(), 3)
        self.assertEqual(len(notifications), 3)
        notification_in_app = Notification.objects.filter(notification_type=Notifications.IN_APP).first()
        self.assertIsNotNone(notification_in_app)
        notification_sms = Notification.objects.filter(notification_type=Notifications.SMS).first()
        self.assertIsNotNone(notification_sms)
        notification_email = Notification.objects.filter(notification_type=Notifications.EMAIL).first()
        self.assertIsNotNone(notification_email)
        self.assertIn(notification_in_app, notifications)
        self.assertIn(notification_sms, notifications)
        self.assertIn(notification_email, notifications)
        for notification in notifications:
            self.assertEqual(notification.user, self.user)
            self.assertFalse(notification.viewed)
            self.assertIsNone(notification.viewed_at)
        self.assertTrue(notification_in_app.sent)
        self.assertFalse(notification_sms.sent)
        self.assertFalse(notification_email.sent)
