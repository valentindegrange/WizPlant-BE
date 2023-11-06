from rest_framework import viewsets

from api.serializers.notification_center import NotificationCenterSerializer
from pyPlants.models import NotificationCenter


class NotificationCenterModelViewSet(viewsets.ModelViewSet):
    queryset = NotificationCenter.objects.all()
    serializer_class = NotificationCenterSerializer
