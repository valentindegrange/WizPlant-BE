from django.test import TestCase, tag
from django.utils import timezone
from freezegun import freeze_time

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

    @freeze_time('2023-01-01')
    def test_notification_created(self):
        # proper notification sent
        notification = self.notification_center_1.send_notification('test')
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(notification.user, self.user_1)
        self.assertEqual(notification.message, 'test')
        self.assertEqual(self.notification_center_1.last_notification_sent, timezone.now())
        # user 2 don't get notifications
        self.assertIsNone(self.notification_center_2.last_notification_sent)
        self.assertFalse(Notification.objects.filter(user=self.user_2).exists())

    def test_notification_viewed(self):
        notification = self.notification_center_1.send_notification('test')
        self.assertFalse(notification.viewed)
        notification.mark_as_viewed()
        self.assertTrue(notification.viewed)
        self.assertIsNotNone(notification.viewed_at)

    def test_notification_not_viewed(self):
        notification = self.notification_center_1.send_notification('test')
        self.assertFalse(notification.viewed)
        self.assertIsNone(notification.viewed_at)
