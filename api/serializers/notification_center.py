from rest_framework import serializers
from pyPlants.models import NotificationCenter


class NotificationCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationCenter
        fields = ['enable_in_app_notifications', 'enable_email_notifications', 'enable_sms_notifications',
                  'preferred_notification_hour', 'last_notification_sent']
        read_only_fields = ['last_notification_sent']
