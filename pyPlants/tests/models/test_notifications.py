from django.test import TestCase, tag
from django.utils import timezone

from pyPlants.models import PlantUser, NotificationCenter, Notification


@tag('notifications')
class NotificationTest(TestCase):
    def setUp(self):
        self.user_1 = PlantUser.objects.create_user(
            email='foo@bar.com'
        )
        self.notification_center_1 = NotificationCenter.objects.create(
            user=self.user_1,
            preferred_notification_hour=12
        )
        self.user_2 = PlantUser.objects.create_user(
            email='bar@bar.com'
        )
        self.notification_center_2 = NotificationCenter.objects.create(
            user=self.user_2,
            preferred_notification_hour=8
        )

    def test_no_notification_created(self):
        self.assertEqual(Notification.objects.count(), 0)
