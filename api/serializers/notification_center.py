from rest_framework import serializers
from pyPlants.models import NotificationCenter


class NotificationCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationCenter
        fields = '__all__'
        # exclude user
