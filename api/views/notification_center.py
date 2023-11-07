from rest_framework import viewsets

from api.serializers.notification_center import NotificationCenterSerializer
from pyPlants.models import NotificationCenter


class NotificationCenterModelViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationCenterSerializer

    def get_queryset(self):
        return NotificationCenter.objects.filter(user=self.request.user)
