from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from django_filters import rest_framework as dj_filters

from api.serializers.notification import NotificationSerializer
from pyPlants.models import Notification


class NotificationModelViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    filter_backends = [dj_filters.DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ('notification_type', 'viewed', 'sent')
    ordering_fields = '__all__'
    ordering = ['-sent_at']

    def get_queryset(self):
        return Notification.objects.all()

    @action(methods=['post'], detail=True)
    def mark_as_viewed(self, request, pk=None):
        notification = self.get_object()
        notification.mark_as_viewed()
        return Response(status=status.HTTP_200_OK)
