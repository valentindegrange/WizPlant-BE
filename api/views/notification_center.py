from rest_framework import viewsets, generics

from api.serializers.notification_center import NotificationCenterSerializer
from pyPlants.models import NotificationCenter


class NotificationCenterViews(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationCenterSerializer

    def get_object(self):
        return NotificationCenter.objects.get(user=self.request.user)

    def update(self, request, *args, **kwargs):
        notification_center = self.get_object()
        serializer = self.get_serializer(notification_center, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return super().update(request, *args, **kwargs)
