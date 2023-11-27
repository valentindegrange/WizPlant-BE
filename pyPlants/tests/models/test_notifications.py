from django.test import TestCase, tag
from django.utils import timezone

from pyPlants.models import PlantUser, NotificationCenter, Notification


@tag('notifications')
class NotificationTest(TestCase):
    def setUp(self):
        self.user_1 = PlantUser.objects.create_user(
            email='foo@bar.com'
        )
        self.notification_center_1 = NotificationCenter.objects.get(user=self.user_1)
        self.notification_center_1.preferred_notification_hour = 12
        self.notification_center_1.save()
        self.user_2 = PlantUser.objects.create_user(
            email='bar@bar.com'
        )
        self.notification_center_2 = NotificationCenter.objects.get(user=self.user_2)
        self.notification_center_2.preferred_notification_hour = 8
        self.notification_center_2.save()

    def test_no_notification_created(self):
        self.assertEqual(Notification.objects.count(), 0)

    def can_change_notification_center(self):
        self.notification_center_1.enable_in_app_notifications = False
        self.notification_center_1.preferred_notification_hour = 15
        self.notification_center_1.save()
        self.assertFalse(self.notification_center_1.enable_in_app_notifications)
