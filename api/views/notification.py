from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers.notification import NotificationSerializer
from pyPlants.models import Notification


class NotificationModelViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    @action(methods=['post'], detail=True)
    def mark_as_viewed(self, request, pk=None):
        notification = self.get_object()
        notification.mark_as_viewed()
        return Response(status=status.HTTP_200_OK)
